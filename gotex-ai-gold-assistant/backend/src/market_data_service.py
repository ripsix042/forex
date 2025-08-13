import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        self.symbol = "GC=F"  # Gold futures symbol for Yahoo Finance
        self.backup_symbol = "XAUUSD=X"  # Alternative gold symbol
        
    def get_live_data(self) -> Dict:
        """Get current live XAUUSD data"""
        try:
            ticker = yf.Ticker(self.symbol)
            info = ticker.info
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                # Try backup symbol
                ticker = yf.Ticker(self.backup_symbol)
                hist = ticker.history(period="1d", interval="1m")
                
            if not hist.empty:
                latest = hist.iloc[-1]
                return {
                    "symbol": "XAUUSD",
                    "price": float(latest['Close']),
                    "open": float(latest['Open']),
                    "high": float(latest['High']),
                    "low": float(latest['Low']),
                    "volume": int(latest['Volume']) if 'Volume' in latest else 0,
                    "timestamp": latest.name.isoformat(),
                    "change": float(latest['Close'] - latest['Open']),
                    "change_percent": float((latest['Close'] - latest['Open']) / latest['Open'] * 100)
                }
            else:
                return self._get_mock_data()
                
        except Exception as e:
            logger.error(f"Error fetching live data: {e}")
            return self._get_mock_data()
    
    def get_historical_data(self, period: str = "1mo", interval: str = "1h") -> List[Dict]:
        """Get historical XAUUSD data"""
        try:
            ticker = yf.Ticker(self.symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                ticker = yf.Ticker(self.backup_symbol)
                hist = ticker.history(period=period, interval=interval)
            
            if not hist.empty:
                data = []
                for timestamp, row in hist.iterrows():
                    data.append({
                        "timestamp": timestamp.isoformat(),
                        "open": float(row['Open']),
                        "high": float(row['High']),
                        "low": float(row['Low']),
                        "close": float(row['Close']),
                        "volume": int(row['Volume']) if 'Volume' in row else 0
                    })
                return data
            else:
                return self._get_mock_historical_data()
                
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return self._get_mock_historical_data()
    
    def _get_mock_data(self) -> Dict:
        """Generate mock live data for testing"""
        base_price = 2000.0
        change = np.random.uniform(-20, 20)
        current_price = base_price + change
        
        return {
            "symbol": "XAUUSD",
            "price": current_price,
            "open": base_price,
            "high": current_price + abs(change) * 0.5,
            "low": current_price - abs(change) * 0.5,
            "volume": np.random.randint(1000, 10000),
            "timestamp": datetime.now().isoformat(),
            "change": change,
            "change_percent": (change / base_price) * 100
        }
    
    def _get_mock_historical_data(self) -> List[Dict]:
        """Generate mock historical data for testing"""
        data = []
        base_price = 2000.0
        current_time = datetime.now() - timedelta(days=30)
        
        for i in range(720):  # 30 days * 24 hours
            price_change = np.random.uniform(-10, 10)
            open_price = base_price + np.random.uniform(-5, 5)
            close_price = open_price + price_change
            high_price = max(open_price, close_price) + np.random.uniform(0, 5)
            low_price = min(open_price, close_price) - np.random.uniform(0, 5)
            
            data.append({
                "timestamp": current_time.isoformat(),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": np.random.randint(1000, 10000)
            })
            
            current_time += timedelta(hours=1)
            base_price = close_price  # Use previous close as next base
        
        return data