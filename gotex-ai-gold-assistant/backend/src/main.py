from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from typing import List, Dict, Any, Optional
import yt_dlp

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
# Fix market service imports to use src prefix
from src.market_data_service import MarketDataService
from src.prediction_engine import PredictionEngine

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

async def process_youtube_video(url: str, file_type: str = "video"):
    """Download and process YouTube video in the background"""
    try:
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'best[height<=720]',  # Download best quality up to 720p
            'outtmpl': os.path.join(UPLOAD_DIR, '%(title)s.%(ext)s'),
            'noplaylist': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Unknown')
            
            # Download the video
            ydl.download([url])
            
            # Find the downloaded file
            downloaded_file = None
            for file in os.listdir(UPLOAD_DIR):
                if video_title.replace('/', '_').replace('\\', '_') in file:
                    downloaded_file = os.path.join(UPLOAD_DIR, file)
                    break
            
            if downloaded_file and os.path.exists(downloaded_file):
                # Process the downloaded video file
                processed_content = content_processor.process_file(downloaded_file, file_type)
                
                # Extract knowledge from the processed content
                if processed_content and "text" in processed_content:
                    metadata = {
                        "filename": os.path.basename(downloaded_file),
                        "content_type": file_type,
                        "source_url": url,
                        "video_title": video_title,
                        "processed_date": processed_content.get("processed_date", ""),
                        "file_size": os.path.getsize(downloaded_file)
                    }
                    
                    # Extract knowledge and store in vector database
                    extracted_knowledge = knowledge_extractor.extract_knowledge(
                        processed_content["text"], metadata
                    )
                    
                    # Save processed results
                    processed_file_path = os.path.join(
                        PROCESSED_DIR, 
                        f"{os.path.basename(downloaded_file)}.json"
                    )
                    
                    with open(processed_file_path, "w") as f:
                        import json
                        json.dump({
                            "processed_content": processed_content,
                            "extracted_knowledge": extracted_knowledge,
                            "metadata": metadata
                        }, f, indent=2)
                        
                return {"success": True, "filename": os.path.basename(downloaded_file), "title": video_title}
            else:
                return {"success": False, "error": "Failed to download video"}
                
    except Exception as e:
        print(f"Error processing YouTube video {url}: {str(e)}")
        return {"success": False, "error": str(e)}

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

@app.post("/upload-youtube/")
async def upload_youtube(background_tasks: BackgroundTasks, 
                        url: str = Form(...), 
                        file_type: str = Form("video")):
    try:
        # Validate YouTube URL
        if not any(domain in url for domain in ['youtube.com', 'youtu.be']):
            return {"error": "Invalid YouTube URL"}, 400
        
        # Ensure the upload directory exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Process the YouTube video in the background
        background_tasks.add_task(process_youtube_video, url, file_type)
        
        return {"url": url, "file_type": file_type, "status": "processing"}
    except Exception as e:
        print(f"Error processing YouTube URL: {str(e)}")
        return {"error": str(e)}, 500

@app.get("/files/")
def list_files():
    try:
        # Get all files from upload directory
        if not os.path.exists(UPLOAD_DIR):
            return JSONResponse(content={"files": []})
            
        files = os.listdir(UPLOAD_DIR)
        
        # Get all processed files (without .json extension)
        processed_files = set()
        if os.path.exists(PROCESSED_DIR):
            for f in os.listdir(PROCESSED_DIR):
                if f.endswith(".json"):
                    # Remove .json extension to get original filename
                    original_filename = f.replace(".json", "")
                    processed_files.add(original_filename)
        
        file_info = []
        for filename in files:
            file_path = os.path.join(UPLOAD_DIR, filename)
            if os.path.isfile(file_path):  # Only include actual files
                processed = filename in processed_files
                
                file_info.append({
                    "filename": filename,
                    "size": os.path.getsize(file_path),
                    "processed": processed,
                    "date_modified": os.path.getmtime(file_path)
                })
        
        return JSONResponse(content={"files": file_info})
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return JSONResponse(content={"files": [], "error": str(e)})

@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(content={"error": "File not found"}, status_code=404)

@app.delete("/files/{filename}")
def delete_file(filename: str):
    try:
        # Delete the original file
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the processed file
        processed_file_path = os.path.join(PROCESSED_DIR, f"{filename}.json")
        if os.path.exists(processed_file_path):
            os.remove(processed_file_path)
        
        return JSONResponse(content={"message": f"File {filename} deleted successfully"})
    except Exception as e:
        print(f"Error deleting file {filename}: {str(e)}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Add this Pydantic model after the imports
class QueryRequest(BaseModel):
    question: str

@app.post("/query/")
async def query(request: QueryRequest):
    """Answer a user's question about gold trading"""
    try:
        result = query_engine.answer_question(request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/query/analytics/")
async def get_query_analytics():
    """Get query analytics data"""
    try:
        analytics = query_engine.get_analytics()
        return {
            "status": "success",
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving analytics: {str(e)}")

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

# Initialize market services (remove the duplicate imports above this)
market_service = MarketDataService()
prediction_engine = PredictionEngine()
@app.get("/market/live")
async def get_live_market_data():
    """Get current live XAUUSD market data"""
    try:
        data = market_service.get_live_data()
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching live data: {str(e)}")

@app.get("/market/history")
async def get_historical_data(period: str = "1mo", interval: str = "1h"):
    """Get historical XAUUSD market data"""
    try:
        data = market_service.get_historical_data(period=period, interval=interval)
        return {"status": "success", "data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")

@app.post("/market/train")
async def train_prediction_model():
    """Train the prediction model with latest data"""
    try:
        # Get historical data for training
        historical_data = market_service.get_historical_data(period="3mo", interval="1h")
        
        if len(historical_data) < 100:
            raise HTTPException(status_code=400, detail="Insufficient historical data for training")
        
        # Train the model
        result = prediction_engine.train_model(historical_data)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return {"status": "success", "training_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training model: {str(e)}")

@app.get("/market/predict")
async def get_predictions(num_predictions: int = 5):
    """Get AI predictions for next candles"""
    try:
        if num_predictions > 24:
            raise HTTPException(status_code=400, detail="Maximum 24 predictions allowed")
        
        # Get recent historical data
        historical_data = market_service.get_historical_data(period="1mo", interval="1h")
        
        # Make predictions
        predictions = prediction_engine.predict_next_candles(historical_data, num_predictions)
        
        if predictions and "error" in predictions[0]:
            raise HTTPException(status_code=500, detail=predictions[0]["error"])
        
        return {
            "status": "success", 
            "predictions": predictions,
            "model_trained": prediction_engine.is_trained
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error making predictions: {str(e)}")

@app.get("/market/status")
async def get_market_status():
    """Get market service status"""
    return {
        "status": "success",
        "market_service": "active",
        "prediction_engine": {
            "trained": prediction_engine.is_trained,
            "features_count": len(prediction_engine.feature_columns) if prediction_engine.feature_columns else 0
        }
    }

if __name__ == "__main__":
    pass
