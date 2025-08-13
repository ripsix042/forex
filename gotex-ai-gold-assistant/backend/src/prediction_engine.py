import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from typing import Dict, List, Tuple, Optional
import joblib
import os
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionEngine:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = []
        self.model_path = "models/xauusd_model.pkl"
        self.scaler_path = "models/xauusd_scaler.pkl"
        
        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)
        
        # Try to load existing model
        self._load_model()
    
    def create_features(self, data: List[Dict]) -> pd.DataFrame:
        """Create technical indicators and features from price data"""
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Basic price features
        df['price_change'] = df['close'] - df['open']
        df['price_range'] = df['high'] - df['low']
        df['body_size'] = abs(df['close'] - df['open'])
        df['upper_shadow'] = df['high'] - df[['open', 'close']].max(axis=1)
        df['lower_shadow'] = df[['open', 'close']].min(axis=1) - df['low']
        
        # Moving averages
        for period in [5, 10, 20, 50]:
            df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
            df[f'ema_{period}'] = df['close'].ewm(span=period).mean()
        
        # Price relative to moving averages
        df['price_vs_sma_20'] = (df['close'] - df['sma_20']) / df['sma_20']
        df['price_vs_ema_20'] = (df['close'] - df['ema_20']) / df['ema_20']
        
        # Volatility indicators
        df['volatility_5'] = df['close'].rolling(window=5).std()
        df['volatility_20'] = df['close'].rolling(window=20).std()
        
        # RSI (Relative Strength Index)
        df['rsi'] = self._calculate_rsi(df['close'])
        
        # MACD
        df['macd'], df['macd_signal'] = self._calculate_macd(df['close'])
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands
        df['bb_upper'], df['bb_lower'], df['bb_middle'] = self._calculate_bollinger_bands(df['close'])
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        
        # Lag features
        for lag in [1, 2, 3, 5]:
            df[f'close_lag_{lag}'] = df['close'].shift(lag)
            df[f'volume_lag_{lag}'] = df['volume'].shift(lag)
        
        # Target variable (next period's close price)
        df['target'] = df['close'].shift(-1)
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        return macd, macd_signal
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, lower_band, sma
    
    def train_model(self, historical_data: List[Dict]) -> Dict:
        """Train the prediction model"""
        try:
            # Create features
            df = self.create_features(historical_data)
            
            # Remove rows with NaN values
            df = df.dropna()
            
            if len(df) < 100:
                raise ValueError("Insufficient data for training (need at least 100 samples)")
            
            # Prepare features and target
            feature_cols = [col for col in df.columns if col not in ['timestamp', 'target']]
            X = df[feature_cols]
            y = df['target']
            
            # Store feature columns for later use
            self.feature_columns = feature_cols
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=False
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Make predictions on test set
            y_pred = self.model.predict(X_test_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            self.is_trained = True
            
            # Save model and scaler
            self._save_model()
            
            logger.info(f"Model trained successfully. MSE: {mse:.2f}, R2: {r2:.4f}")
            
            return {
                "status": "success",
                "mse": mse,
                "r2_score": r2,
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "features_count": len(feature_cols)
            }
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def predict_next_candles(self, historical_data: List[Dict], num_predictions: int = 5) -> List[Dict]:
        """Predict next few candles"""
        if not self.is_trained:
            return [{"error": "Model not trained yet"}]
        
        try:
            # Create features from historical data
            df = self.create_features(historical_data)
            df = df.dropna()
            
            if len(df) == 0:
                return [{"error": "Insufficient data for prediction"}]
            
            predictions = []
            current_data = df.copy()
            
            for i in range(num_predictions):
                # Get the latest features
                latest_features = current_data[self.feature_columns].iloc[-1:]
                
                # Scale features
                latest_scaled = self.scaler.transform(latest_features)
                
                # Make prediction
                predicted_price = self.model.predict(latest_scaled)[0]
                
                # Create prediction timestamp
                last_timestamp = pd.to_datetime(current_data['timestamp'].iloc[-1])
                next_timestamp = last_timestamp + timedelta(hours=1)
                
                # Estimate other OHLC values based on predicted close
                last_close = current_data['close'].iloc[-1]
                price_change = predicted_price - last_close
                
                # Simple estimation for OHLC
                predicted_open = last_close
                predicted_high = max(predicted_open, predicted_price) + abs(price_change) * 0.3
                predicted_low = min(predicted_open, predicted_price) - abs(price_change) * 0.3
                
                prediction = {
                    "timestamp": next_timestamp.isoformat(),
                    "open": round(predicted_open, 2),
                    "high": round(predicted_high, 2),
                    "low": round(predicted_low, 2),
                    "close": round(predicted_price, 2),
                    "volume": int(current_data['volume'].iloc[-5:].mean()),  # Average recent volume
                    "confidence": max(0.1, 1.0 - (i * 0.15))  # Decreasing confidence
                }
                
                predictions.append(prediction)
                
                # Add this prediction to current_data for next iteration
                new_row = {
                    'timestamp': next_timestamp,
                    'open': predicted_open,
                    'high': predicted_high,
                    'low': predicted_low,
                    'close': predicted_price,
                    'volume': prediction['volume']
                }
                
                # Create features for the new row and append
                new_df = pd.DataFrame([new_row])
                extended_data = pd.concat([current_data, new_df], ignore_index=True)
                current_data = self.create_features(extended_data.to_dict('records'))
                current_data = current_data.dropna()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            return [{"error": str(e)}]
    
    def _save_model(self):
        """Save trained model and scaler"""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(self.feature_columns, "models/feature_columns.pkl")
            logger.info("Model saved successfully")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def _load_model(self):
        """Load existing model and scaler"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.feature_columns = joblib.load("models/feature_columns.pkl")
                self.is_trained = True
                logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.is_trained = False