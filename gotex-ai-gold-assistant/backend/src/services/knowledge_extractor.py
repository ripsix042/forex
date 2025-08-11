import re
import json
import os
from typing import Dict, List, Any, Optional

from src.config import OPENAI_API_KEY, PROCESSED_DIR
from src.services.vector_store import vector_store

# Optional imports with fallbacks
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class KnowledgeExtractor:
    def __init__(self):
        self.openai_available = OPENAI_API_KEY is not None and OPENAI_API_KEY != "your_openai_api_key" and OPENAI_AVAILABLE
        if self.openai_available and OPENAI_AVAILABLE:
            try:
                openai.api_key = OPENAI_API_KEY
            except Exception as e:
                print(f"Error initializing OpenAI API: {e}")
                self.openai_available = False
        
        # Trading concepts to identify
        self.trading_concepts = [
            "candlestick pattern", "support level", "resistance level", 
            "trend line", "moving average", "RSI", "MACD", "Fibonacci",
            "breakout", "pullback", "reversal", "continuation", "divergence",
            "volume analysis", "price action", "chart pattern", "indicator",
            "oscillator", "momentum", "volatility", "market structure"
        ]
    
    def extract_knowledge(self, text: str, source_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Extract trading knowledge from text"""
        if self.openai_available:
            return self._extract_with_openai(text, source_metadata)
        else:
            return self._extract_with_rules(text, source_metadata)
    
    def _extract_with_openai(self, text: str, source_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Use OpenAI to extract trading knowledge"""
        try:
            prompt = f"""Extract gold trading knowledge from the following text. 
            Identify key concepts like candlestick patterns, support/resistance levels, 
            indicators, trend strategies, etc. Format the output as JSON with these fields:
            - concepts: list of trading concepts identified
            - patterns: list of specific patterns mentioned
            - rules: list of trading rules or strategies
            - indicators: list of technical indicators mentioned
            - summary: brief summary of the trading knowledge
            
            Text: {text}
            
            JSON Output:"""
            
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=prompt,
                max_tokens=500,
                temperature=0.3,
                top_p=1.0
            )
            
            # Parse the JSON response
            try:
                extracted_data = json.loads(response.choices[0].text.strip())
            except json.JSONDecodeError:
                # Fallback to rule-based extraction if JSON parsing fails
                extracted_data = self._extract_with_rules(text, source_metadata)
                extracted_data["note"] = "OpenAI extraction failed, used rule-based fallback"
            
            # Store in vector database
            for concept in extracted_data.get("concepts", []):
                vector_store.add_item(
                    concept,
                    {
                        "type": "trading_concept",
                        "source": source_metadata.get("filename", "unknown"),
                        "source_type": source_metadata.get("content_type", "unknown"),
                        "concept": concept
                    }
                )
            
            # Store the full extraction result
            extracted_data["source_metadata"] = source_metadata
            return extracted_data
            
        except Exception as e:
            # Fallback to rule-based extraction
            result = self._extract_with_rules(text, source_metadata)
            result["error"] = str(e)
            return result
    
    def _extract_with_rules(self, text: str, source_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Use rule-based approach to extract trading knowledge"""
        result = {
            "concepts": [],
            "patterns": [],
            "rules": [],
            "indicators": [],
            "summary": "Extracted using rule-based approach"
        }
        
        # Look for trading concepts
        for concept in self.trading_concepts:
            if re.search(r'\b' + re.escape(concept) + r'\b', text.lower()):
                result["concepts"].append(concept)
        
        # Look for candlestick patterns
        candlestick_patterns = [
            "doji", "hammer", "hanging man", "engulfing", "harami",
            "morning star", "evening star", "shooting star", "marubozu"
        ]
        for pattern in candlestick_patterns:
            if re.search(r'\b' + re.escape(pattern) + r'\b', text.lower()):
                result["patterns"].append(pattern)
        
        # Look for indicators
        indicators = [
            "RSI", "MACD", "moving average", "bollinger", "stochastic",
            "ATR", "OBV", "ichimoku", "ADX", "CCI", "MFI"
        ]
        for indicator in indicators:
            if re.search(r'\b' + re.escape(indicator) + r'\b', text.lower()):
                result["indicators"].append(indicator)
        
        # Extract sentences that might contain trading rules
        sentences = re.split(r'[.!?]\s+', text)
        for sentence in sentences:
            if re.search(r'\b(if|when|always|never|buy|sell|trade|entry|exit)\b', sentence.lower()):
                # Clean up the sentence
                clean_sentence = sentence.strip()
                if clean_sentence and len(clean_sentence) > 10:
                    result["rules"].append(clean_sentence)
        
        # Limit the number of rules to avoid overwhelming results
        result["rules"] = result["rules"][:5]
        
        # Store in vector database
        for concept in result["concepts"]:
            vector_store.add_item(
                concept,
                {
                    "type": "trading_concept",
                    "source": source_metadata.get("filename", "unknown"),
                    "source_type": source_metadata.get("content_type", "unknown"),
                    "concept": concept
                }
            )
        
        result["source_metadata"] = source_metadata
        return result

# Create a singleton instance
knowledge_extractor = KnowledgeExtractor()