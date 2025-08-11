# Gotex AI Gold Trading Assistant

## Current Implementation Status

This is the initial implementation of the Gotex AI Gold Trading Assistant. The project is currently in **Phase 1** of the roadmap, with basic functionality for file uploads and simple gold trading queries.

### Implemented Features

#### Backend (FastAPI)
- File upload endpoint with support for different file types (Chart/Image, PDF Document, CSV Data, Excel Spreadsheet)
- File listing and retrieval endpoints
- Basic query endpoint for gold trading questions using a simple knowledge base

#### Frontend (React)
- Modern, responsive UI with custom styling
- File upload component with file type selection
- "Ask Gotex" interface for querying the AI about gold trading
- Suggested questions for user guidance
- Display of uploaded resources with file type indicators

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

The current implementation serves as a foundation for the full Gotex AI Gold Trading Assistant. Future development will focus on:

1. Implementing the AI learning engine for processing educational content
2. Adding vector storage for knowledge retention
3. Integrating live chart data and prediction capabilities
4. Enhancing the UI with chart visualization

Refer to the main project README for the complete roadmap and feature set.