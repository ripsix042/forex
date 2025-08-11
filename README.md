# Gotex – The AI Gold Trading Assistant

## Description
Gotex is an advanced AI assistant built to learn trading strategies from educational content (videos, images, documents) and use that knowledge to predict the next 10 five-minute candles for the XAU/USD (gold) market. It simulates expert human learning and prediction by processing multimedia content, analyzing real-time charts, and improving continuously through user feedback.

## Main Objectives

### Learn from Content
- Accepts YouTube video links, PDFs, images, and screenshots of trading materials (e.g. from BabyPips, TradingView, social media)
- Understands audio, transcribed subtitles, and charts in videos/images
- Extracts and stores trading concepts: candlestick patterns, support/resistance, indicators, trend strategies, etc.

### Retain Knowledge
- Learns continuously over time and does not forget previous lessons
- Capable of incremental learning: each new input builds on the existing memory without overwriting it

### Predict Market Movement
- Focuses on XAUUSD (gold)
- Predicts the next 10 five-minute candles using learned strategies
- Accepts live chart data and processes it to make forecasts

### Front-End Dashboard
- Drag-and-drop interface to upload:
  - Images (charts, screenshots)
  - Videos (MP4 or YouTube links)
  - PDFs/documents
- View predictions in chart form with confidence scores
- Option to query Gotex (e.g. "Why this prediction?" or "Explain the current pattern")

## Features

### A. Training Input System
- Video/audio transcription to extract strategies and market rules
- OCR (Optical Character Recognition) for chart images
- Embeds screenshots and trading advice into vector memory (e.g., using FAISS or Pinecone)
- Parses trading-specific concepts (EMA, RSI, support zones, fake-outs)

### B. Persistent Memory Engine
- Memory model stores historical training
- New files incrementally enhance the AI's strategy map
- No knowledge loss between training sessions

### C. Real-Time Prediction Engine
- Connects to live market data (e.g., via broker or chart API)
- Uses learned strategies to predict next 10 candles (5-min interval)
- Shows the predicted price levels, wick/high/low, and confidence range

### D. Frontend UI
- Upload zone for content (files, links)
- Live chart viewer with:
  - Real-time XAUUSD candles
  - Predicted candles overlaid
  - Timeline of learned strategies (with edit or delete options)
- Query box (ask "Why did gold drop here?", etc.)

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React.js / Next.js + Tailwind CSS |
| Backend | Node.js / Python (FastAPI or Flask) |
| AI/NLP | OpenAI GPT-4o / LLaMA / Whisper (for audio) |
| Charting | TradingView Widget / Lightweight Charts |
| Prediction Model | LSTM / Transformer + Reinforcement Learning |
| Storage | Pinecone (vector memory), PostgreSQL (metadata), S3 (assets) |
| Training Data Tools | Whisper (audio), CLIP (images), LangChain (retrieval) |

## Roadmap (Milestones)

### Phase 1: Core Setup
- Project setup (frontend + backend)
- Upload + ingest educational materials (video, image, PDF)
- Whisper transcription & CLIP image recognition

### Phase 2: Learning Engine
- Store extracted knowledge in long-term memory
- Summarize & visualize what AI has learned
- Test knowledge with quizzes or mock predictions

### Phase 3: Live Chart Analysis
- Integrate live XAUUSD data feed
- Use learned patterns to predict next 10 candles (5-min each)
- Visual prediction chart (candlesticks + confidence)

### Phase 4: Frontend UI
- Dashboard for uploading content
- View learning history + predicted candles
- "Ask Gotex" chatbot interface

### Phase 5: Continuous Learning & Feedback
- Enable re-training from new videos/images
- Feedback loop to improve predictions over time
- Memory control (edit/remove learned items)

## Example Use Case Flow
1. You upload 10 BabyPips videos + 5 chart screenshots
2. Gotex transcribes, learns, and stores strategies
3. You connect Gotex to a live XAUUSD feed
4. Gotex predicts the first 10 upcoming 5-minute candles
5. You ask, "Why is the price predicted to go up?" and it answers using what it learned