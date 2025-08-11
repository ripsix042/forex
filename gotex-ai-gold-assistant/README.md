# Gotex AI Gold Trading Assistant

## Current Implementation Status

The Gotex AI Gold Trading Assistant is now in **Phase 2** of the roadmap, with the Learning Engine implementation added to the initial file upload and query functionality.

### Implemented Features

#### Backend (FastAPI)
- File upload endpoint with support for different file types (Chart/Image, PDF Document, CSV Data, Excel Spreadsheet)
- File listing and retrieval endpoints with processing status
- Advanced query engine using vector search and fallback knowledge base
- Content processing pipeline for different file types
- Knowledge extraction system to identify trading concepts, patterns, and indicators
- Learning visualization with statistics and charts
- Vector database integration (Pinecone with FAISS fallback)

#### Frontend (React)
- Modern, responsive UI with custom styling
- File upload component with file type selection
- "Ask Gotex" interface for querying the AI about gold trading
- Suggested questions for user guidance
- Display of uploaded resources with file type indicators
- Learning Engine visualization dashboard with:
  - Learning statistics summary
  - Trading concepts, patterns, and indicators tables
  - Learning timeline visualization
  - Charts for concept frequency and learning progress

## Running the Application

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd src
uvicorn main:app --reload
```

The backend server will run at http://127.0.0.1:8000

### Frontend
```bash
cd frontend
npm install
npm start
```

The frontend application will run at http://localhost:3000

## Next Steps

With the Learning Engine now implemented, future development will focus on:

1. Enhancing the content processing pipeline with more advanced OCR and document parsing
2. Implementing YouTube video processing with audio transcription
3. Integrating live chart data and prediction capabilities (Phase 3)
4. Adding user feedback mechanisms to improve learning
5. Implementing automated testing for the learning engine components

Refer to the main project README for the complete roadmap and feature set.