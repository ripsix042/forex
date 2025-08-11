import json
from typing import Dict, List, Any, Optional

from src.config import OPENAI_API_KEY
from src.services.vector_store import vector_store

# Optional imports with fallbacks
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class QueryEngine:
    def __init__(self):
        self.openai_available = OPENAI_API_KEY is not None and OPENAI_API_KEY != "your_openai_api_key" and OPENAI_AVAILABLE
        if self.openai_available:
            try:
                openai.api_key = OPENAI_API_KEY
            except Exception as e:
                print(f"Error initializing OpenAI API: {e}")
                self.openai_available = False
        
        # Fallback knowledge base for when no relevant info is found
        self.fallback_knowledge = {
            "gold price": "Gold prices fluctuate based on market conditions, economic indicators, and geopolitical events. As of the last update, gold was trading around $2,000 per ounce, but this can change rapidly.",
            "investment": "Gold is considered a safe-haven asset that can help diversify investment portfolios and hedge against inflation and currency devaluation.",
            "trading hours": "Gold trades nearly 24 hours a day on markets around the world, with the main trading centers being London, New York, and Shanghai.",
            "factors": "Key factors affecting gold prices include interest rates, inflation, currency values (especially USD), central bank policies, and global economic uncertainty.",
            "etf": "Gold ETFs (Exchange-Traded Funds) allow investors to gain exposure to gold prices without physically owning gold. Popular options include GLD and IAU.",
            "physical gold": "Physical gold can be purchased as coins, bars, or jewelry. When buying physical gold, consider purity (measured in karats), premium over spot price, and storage costs.",
            "technical analysis": "Common technical indicators for gold trading include moving averages, RSI (Relative Strength Index), MACD (Moving Average Convergence Divergence), and Fibonacci retracement levels.",
            "seasonal patterns": "Gold often shows seasonal patterns, with prices typically stronger during certain months like September and weaker during others."
        }
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a user's question about gold trading"""
        # Search for relevant information in the vector store
        search_results = vector_store.search(question, top_k=5)
        
        if search_results and len(search_results) > 0:
            return self._generate_answer_from_search(question, search_results)
        else:
            return self._generate_fallback_answer(question)
    
    def _generate_answer_from_search(self, question: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate an answer based on search results"""
        if self.openai_available:
            return self._generate_with_openai(question, search_results)
        else:
            return self._generate_with_rules(question, search_results)
    
    def _generate_with_openai(self, question: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use OpenAI to generate an answer"""
        if not OPENAI_AVAILABLE:
            # Fallback to rule-based generation if OpenAI is not available
            result = self._generate_with_rules(question, search_results)
            result["error"] = "OpenAI module not available"
            return result
            
        try:
            # Prepare context from search results
            context = "\n\n".join([f"Source {i+1}: {result.get('text', '')}" 
                                for i, result in enumerate(search_results)])
            
            prompt = f"""Answer the following question about gold trading based on the provided context.
            If the context doesn't contain relevant information, use your general knowledge about gold trading.
            
            Context:
            {context}
            
            Question: {question}
            
            Answer:"""
            
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=300,
                temperature=0.5,
                top_p=1.0
            )
            
            answer = response.choices[0].text.strip()
            
            return {
                "answer": answer,
                "sources": [{
                    "filename": result.get("metadata", {}).get("filename", "unknown"),
                    "relevance": result.get("score", 0)
                } for result in search_results[:3]],
                "method": "ai_generated"
            }
            
        except Exception as e:
            # Fallback to rule-based generation
            result = self._generate_with_rules(question, search_results)
            result["error"] = str(e)
            return result
    
    def _generate_with_rules(self, question: str, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use rule-based approach to generate an answer"""
        # Extract the most relevant text
        most_relevant = search_results[0] if search_results else None
        
        if most_relevant and "text" in most_relevant:
            answer = most_relevant["text"]
            if len(answer) > 300:
                # Truncate to a reasonable length
                answer = answer[:300] + "..."
        else:
            # Use fallback knowledge base
            return self._generate_fallback_answer(question)
        
        return {
            "answer": answer,
            "sources": [{
                "filename": result.get("metadata", {}).get("filename", "unknown"),
                "relevance": result.get("score", 0)
            } for result in search_results[:3]],
            "method": "rule_based"
        }
    
    def _generate_fallback_answer(self, question: str) -> Dict[str, Any]:
        """Generate a fallback answer when no relevant information is found"""
        question = question.lower()
        
        # Check for keywords in the fallback knowledge base
        for keyword, answer in self.fallback_knowledge.items():
            if keyword in question:
                return {
                    "answer": answer,
                    "sources": [],
                    "method": "fallback_knowledge_base"
                }
        
        # Default response if no keywords match
        return {
            "answer": "I don't have specific information about that aspect of gold trading. Consider asking about gold prices, investment strategies, trading hours, price factors, ETFs, physical gold, technical analysis, or seasonal patterns.",
            "sources": [],
            "method": "default_response"
        }

# Create a singleton instance
query_engine = QueryEngine()