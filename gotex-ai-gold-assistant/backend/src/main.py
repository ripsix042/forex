from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from typing import List, Dict, Any, Optional

# Set up paths for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our services
from src.services.vector_store import vector_store
from src.services.content_processor import content_processor
from src.services.knowledge_extractor import knowledge_extractor
from src.services.query_engine import query_engine
from src.services.learning_visualizer import learning_visualizer
from src.config import UPLOAD_DIR, PROCESSED_DIR

# Create directories if they don't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:3000"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Gotex - The AI Gold Trading Assistant"}

from fastapi.responses import JSONResponse, FileResponse

async def process_file(file_path: str, file_type: str):
    """Process uploaded file in the background"""
    try:
        # Process the content based on file type
        processed_content = content_processor.process_file(file_path, file_type)
        
        # Extract knowledge from the processed content
        if processed_content and "text" in processed_content:
            metadata = {
                "filename": os.path.basename(file_path),
                "content_type": file_type,
                "processed_date": processed_content.get("processed_date", ""),
                "file_size": os.path.getsize(file_path)
            }
            
            # Extract knowledge and store in vector database
            extracted_knowledge = knowledge_extractor.extract_knowledge(
                processed_content["text"], metadata
            )
            
            # Save processed results
            processed_file_path = os.path.join(
                PROCESSED_DIR, 
                f"{os.path.basename(file_path)}.json"
            )
            
            with open(processed_file_path, "w") as f:
                import json
                json.dump({
                    "processed_content": processed_content,
                    "extracted_knowledge": extracted_knowledge,
                    "metadata": metadata
                }, f, indent=2)
                
            return True
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        return False

@app.post("/upload/")
async def upload_file(background_tasks: BackgroundTasks, 
                     file: UploadFile = File(...), 
                     file_type: str = Form("document")):
    try:
        # Ensure the upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Create the full file path
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        print(f"Saving file to: {file_location}")
        
        # Save the uploaded file
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Process the file in the background
        background_tasks.add_task(process_file, file_location, file_type)
        
        return {"filename": file.filename, "file_type": file_type, "status": "processing"}
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/files/")
def list_files():
    files = os.listdir(UPLOAD_DIR)
    processed_files = [f.replace(".json", "") for f in os.listdir(PROCESSED_DIR) if f.endswith(".json")]
    
    file_info = []
    for filename in files:
        file_path = os.path.join(UPLOAD_DIR, filename)
        processed = filename in processed_files
        
        file_info.append({
            "filename": filename,
            "size": os.path.getsize(file_path),
            "processed": processed,
            "date_modified": os.path.getmtime(file_path)
        })
    
    return JSONResponse(content={"files": file_info})

@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(content={"error": "File not found"}, status_code=404)

@app.post("/query/")
async def query(question: str = Form(...)):
    # Use the query engine to answer the question
    result = query_engine.answer_question(question)
    
    return result

@app.get("/learning/stats/")
def get_learning_stats():
    """Get statistics about the system's learning progress"""
    stats = learning_visualizer.generate_learning_stats()
    return JSONResponse(content=stats)

@app.get("/learning/charts/concepts/")
def get_concept_chart():
    """Generate and return a chart of the most common trading concepts"""
    try:
        chart_path = learning_visualizer.generate_concept_chart()
        if chart_path == "No concepts found":
            return JSONResponse(content={"error": "No concepts found"}, status_code=404)
        return FileResponse(chart_path)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/learning/charts/timeline/")
def get_timeline_chart():
    """Generate and return a timeline chart of learning progress"""
    try:
        chart_path = learning_visualizer.generate_learning_timeline_chart()
        if chart_path == "No timeline data found":
            return JSONResponse(content={"error": "No timeline data found"}, status_code=404)
        return FileResponse(chart_path)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
