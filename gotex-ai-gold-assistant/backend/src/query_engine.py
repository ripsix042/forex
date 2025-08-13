import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from vector_store import VectorStore
from openai import OpenAI

class QueryEngine:
    def __init__(self, vector_store: VectorStore, openai_api_key: Optional[str] = None):
        self.vector_store = vector_store
        self.openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
        self.analytics_file = "query_analytics.json"
        self.load_analytics()
        
        # Enhanced fallback knowledge base
        self.fallback_knowledge = {
            "gold price": "Gold prices are influenced by various factors including inflation, currency fluctuations, central bank policies, geopolitical events, and supply-demand dynamics. Historical data shows gold often performs well during economic uncertainty.",
            "inflation": "Gold is traditionally considered a hedge against inflation. When inflation rises, the purchasing power of currency decreases, making gold more attractive as a store of value. However, this relationship can vary based on other economic factors.",
            "trading strategies": "Common gold trading strategies include: 1) Dollar-cost averaging for long-term investment, 2) Technical analysis using support/resistance levels, 3) News-based trading around economic announcements, 4) Seasonal patterns (gold often performs well in certain months), and 5) Portfolio diversification (typically 5-10% allocation).",
            "central bank": "Central banks significantly impact gold prices through monetary policy. Lower interest rates typically support gold prices as they reduce the opportunity cost of holding non-yielding assets. Quantitative easing and currency devaluation policies often drive investors toward gold.",
            "volatility": "Gold volatility is influenced by market sentiment, economic data releases, geopolitical tensions, currency movements (especially USD), and trading volumes. During crisis periods, volatility typically increases as investors seek safe-haven assets.",
            "best time": "There's no universally 'best' time to buy gold, but consider: 1) During economic uncertainty or market downturns, 2) When inflation expectations rise, 3) During currency weakness, 4) As part of regular portfolio rebalancing, and 5) When gold is oversold based on technical analysis.",
            "market trends": "Current gold market trends should be analyzed considering: global economic conditions, central bank policies, inflation rates, currency movements, geopolitical events, and technical chart patterns. Always consult recent market data and professional analysis.",
            "investment": "Gold can be invested in through: 1) Physical gold (coins, bars), 2) Gold ETFs, 3) Gold mining stocks, 4) Gold futures and options, 5) Gold mutual funds. Each method has different risk profiles, costs, and liquidity characteristics."
        }
    
    def load_analytics(self):
        """Load query analytics from file"""
        try:
            if os.path.exists(self.analytics_file):
                with open(self.analytics_file, 'r') as f:
                    self.analytics = json.load(f)
            else:
                self.analytics = {
                    "total_queries": 0,
                    "query_history": [],
                    "popular_topics": {},
                    "daily_stats": {}
                }
        except Exception as e:
            print(f"Error loading analytics: {e}")
            self.analytics = {
                "total_queries": 0,
                "query_history": [],
                "popular_topics": {},
                "daily_stats": {}
            }
    
    def save_analytics(self):
        """Save query analytics to file"""
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.analytics, f, indent=2)
        except Exception as e:
            print(f"Error saving analytics: {e}")
    
    def track_query(self, question: str, answer: str, sources: List[str]):
        """Track query for analytics"""
        try:
            now = datetime.now()
            today = now.strftime("%Y-%m-%d")
            
            # Update total queries
            self.analytics["total_queries"] += 1
            
            # Add to history (keep last 100)
            query_record = {
                "timestamp": now.isoformat(),
                "question": question,
                "answer_length": len(answer),
                "sources_count": len(sources),
                "date": today
            }
            self.analytics["query_history"].append(query_record)
            if len(self.analytics["query_history"]) > 100:
                self.analytics["query_history"] = self.analytics["query_history"][-100:]
            
            # Update popular topics (extract keywords)
            keywords = self.extract_keywords(question.lower())
            for keyword in keywords:
                if keyword in self.analytics["popular_topics"]:
                    self.analytics["popular_topics"][keyword] += 1
                else:
                    self.analytics["popular_topics"][keyword] = 1
            
            # Update daily stats
            if today in self.analytics["daily_stats"]:
                self.analytics["daily_stats"][today] += 1
            else:
                self.analytics["daily_stats"][today] = 1
            
            # Keep only last 30 days of daily stats
            if len(self.analytics["daily_stats"]) > 30:
                sorted_dates = sorted(self.analytics["daily_stats"].keys())
                for old_date in sorted_dates[:-30]:
                    del self.analytics["daily_stats"][old_date]
            
            self.save_analytics()
        except Exception as e:
            print(f"Error tracking query: {e}")
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from query text"""
        keywords = []
        keyword_map = {
            "price": ["price", "cost", "value", "worth"],
            "trading": ["trading", "trade", "buy", "sell", "invest"],
            "strategy": ["strategy", "strategies", "approach", "method"],
            "inflation": ["inflation", "inflat"],
            "central bank": ["central bank", "fed", "federal reserve", "monetary policy"],
            "volatility": ["volatility", "volatile", "fluctuation", "swing"],
            "market": ["market", "trend", "analysis"],
            "investment": ["investment", "invest", "portfolio", "allocation"]
        }
        
        for topic, terms in keyword_map.items():
            if any(term in text for term in terms):
                keywords.append(topic)
        
        return keywords
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get query analytics data"""
        # Get top 10 popular topics
        top_topics = sorted(
            self.analytics["popular_topics"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "total_queries": self.analytics["total_queries"],
            "recent_queries_count": len(self.analytics["query_history"]),
            "top_topics": dict(top_topics),
            "daily_stats": self.analytics["daily_stats"],
            "recent_queries": self.analytics["query_history"][-10:]  # Last 10 queries
        }
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """Answer a user's question about gold trading"""
        try:
            # Search for relevant information
            search_results = self.vector_store.search(question, top_k=5)
            
            sources = []
            context_parts = []
            
            if search_results:
                for result in search_results:
                    context_parts.append(result['content'])
                    if 'source' in result:
                        sources.append(result['source'])
                    elif 'filename' in result:
                        sources.append(result['filename'])
            
            context = "\n\n".join(context_parts)
            
            # Generate answer
            if context and self.openai_client:
                answer = self._generate_openai_answer(question, context)
            elif context:
                answer = self._generate_rule_based_answer(question, context)
            else:
                answer = self._get_fallback_answer(question)
                sources = ["Built-in knowledge base"]
            
            # Track the query
            self.track_query(question, answer, sources)
            
            return {
                "answer": answer,
                "sources": sources,
                "context_found": len(context_parts) > 0
            }
            
        except Exception as e:
            print(f"Error answering question: {e}")
            fallback_answer = self._get_fallback_answer(question)
            return {
                "answer": fallback_answer,
                "sources": ["Built-in knowledge base"],
                "context_found": False
            }
    
    def _generate_openai_answer(self, question: str, context: str) -> str:
        """Generate answer using OpenAI"""
        try:
            prompt = f"""Based on the following context about gold trading, please answer the user's question.
            
Context:
            {context}
            
Question: {question}
            
Please provide a helpful, accurate answer based on the context. If the context doesn't contain enough information to fully answer the question, say so and provide what information you can."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant specializing in gold trading and investment advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error with OpenAI: {e}")
            return self._generate_rule_based_answer(question, context)
    
    def _generate_rule_based_answer(self, question: str, context: str) -> str:
        """Generate answer using rule-based approach"""
        # Simple rule-based response
        answer_parts = []
        
        if context:
            # Extract relevant sentences from context
            sentences = context.split('. ')
            relevant_sentences = []
            
            question_words = set(question.lower().split())
            for sentence in sentences[:5]:  # Limit to first 5 sentences
                sentence_words = set(sentence.lower().split())
                if question_words.intersection(sentence_words):
                    relevant_sentences.append(sentence.strip())
            
            if relevant_sentences:
                answer_parts.append("Based on the available information:")
                answer_parts.extend(relevant_sentences[:3])  # Top 3 relevant sentences
            else:
                answer_parts.append("Here's what I found in the documents:")
                answer_parts.append(context[:500] + "..." if len(context) > 500 else context)
        
        return " ".join(answer_parts)
    
    def _get_fallback_answer(self, question: str) -> str:
        """Get fallback answer from knowledge base"""
        question_lower = question.lower()
        
        # Find the best matching topic
        best_match = None
        max_matches = 0
        
        for topic, answer in self.fallback_knowledge.items():
            matches = sum(1 for word in topic.split() if word in question_lower)
            if matches > max_matches:
                max_matches = matches
                best_match = answer
        
        if best_match:
            return f"{best_match}\n\nNote: This answer is based on general knowledge. For more specific information, please upload relevant documents about gold trading."
        else:
            return "I don't have specific information about that topic in my current knowledge base. Please try uploading relevant documents about gold trading, or ask about topics like gold prices, trading strategies, inflation effects, or market trends."