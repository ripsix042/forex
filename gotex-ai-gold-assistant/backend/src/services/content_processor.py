import os
import re
import json
from typing import Dict, List, Any, Optional
from PIL import Image
import requests
from urllib.parse import urlparse

from src.config import UPLOAD_DIR, PROCESSED_DIR
from src.services.vector_store import vector_store

# Optional imports with fallbacks
try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False

class ContentProcessor:
    def __init__(self):
        self.supported_file_types = {
            "image": [".jpg", ".jpeg", ".png", ".gif"],
            "document": [".pdf", ".txt", ".doc", ".docx"],
            "data": [".csv", ".xlsx", ".xls"],
            "video": [".mp4", ".avi", ".mov", ".mkv"]
        }
        
        # Create directories if they don't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    def process_file(self, filename: str, file_type: str) -> Dict[str, Any]:
        """Process an uploaded file based on its type"""
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(file_path):
            return {"error": f"File {filename} not found"}
        
        # Determine file extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower()
        
        # Process based on file type
        if ext in self.supported_file_types["image"]:
            return self._process_image(file_path, filename, file_type)
        elif ext in self.supported_file_types["document"]:
            return self._process_document(file_path, filename, file_type)
        elif ext in self.supported_file_types["data"]:
            return self._process_data_file(file_path, filename, file_type)
        elif ext in self.supported_file_types["video"]:
            return self._process_video(file_path, filename, file_type)
        else:
            return {"error": f"Unsupported file type: {ext}"}
    
    def _process_document(self, file_path: str, filename: str, file_type: str) -> Dict[str, Any]:
        """Process document files"""
        try:
            # For now, return a basic text extraction
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                "text": content,
                "processed_date": str(os.path.getmtime(file_path)),
                "content_type": "document",
                "status": "success"
            }
        except Exception as e:
            return {"error": f"Error processing document: {str(e)}"}
    
    def _process_data_file(self, file_path: str, filename: str, file_type: str) -> Dict[str, Any]:
        """Process data files (CSV, Excel)"""
        try:
            if not PANDAS_AVAILABLE:
                return {"error": "Data processing requires pandas which is not installed"}
            
            # Read the file based on extension
            _, ext = os.path.splitext(filename)
            if ext.lower() == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Convert to text representation
            text_content = f"Data file summary:\nColumns: {', '.join(df.columns)}\nRows: {len(df)}\n\nFirst few rows:\n{df.head().to_string()}"
            
            return {
                "text": text_content,
                "processed_date": str(os.path.getmtime(file_path)),
                "content_type": "data",
                "status": "success"
            }
        except Exception as e:
            return {"error": f"Error processing data file: {str(e)}"}
    
    def _process_video(self, file_path: str, filename: str, file_type: str) -> Dict[str, Any]:
        """Process video files"""
        try:
            # For now, return basic file info as text
            file_size = os.path.getsize(file_path)
            text_content = f"Video file: {filename}\nSize: {file_size} bytes\nProcessed for trading analysis."
            
            return {
                "text": text_content,
                "processed_date": str(os.path.getmtime(file_path)),
                "content_type": "video",
                "status": "success"
            }
        except Exception as e:
            return {"error": f"Error processing video: {str(e)}"}
    
    def process_youtube_link(self, url: str) -> Dict[str, Any]:
        """Process a YouTube video link"""
        # Validate YouTube URL
        if not self._is_valid_youtube_url(url):
            return {"error": "Invalid YouTube URL"}
        
        if not YTDLP_AVAILABLE:
            return {
                "status": "error",
                "message": "YouTube processing requires yt-dlp which is not installed",
                "url": url
            }
        
        # This is a placeholder - actual implementation would use yt-dlp and Whisper
        return {
            "status": "pending",
            "message": "YouTube video processing will be implemented soon",
            "url": url
        }
    
    def _is_valid_youtube_url(self, url: str) -> bool:
        """Check if URL is a valid YouTube URL"""
        parsed_url = urlparse(url)
        return (
            parsed_url.netloc in ["youtube.com", "www.youtube.com", "youtu.be"] and
            ("watch" in parsed_url.path or parsed_url.netloc == "youtu.be")
        )
    
    def _process_image(self, file_path: str, filename: str, file_type: str) -> Dict[str, Any]:
        """Process an image file using OCR and store in vector database"""
        try:
            # Open the image
            image = Image.open(file_path)
            
            # Check if OCR is available
            if not PYTESSERACT_AVAILABLE:
                return {
                    "status": "partial",
                    "message": "Image processed but OCR is not available (pytesseract not installed)",
                    "metadata": {
                        "filename": filename,
                        "file_type": file_type,
                        "content_type": "image",
                        "source": "uploaded_file"
                    }
                }
            
            # Use OCR to extract text from image
            extracted_text = pytesseract.image_to_string(image)
            
            # Clean up the extracted text
            cleaned_text = self._clean_text(extracted_text)
            
            if not cleaned_text:
                return {"warning": "No text could be extracted from the image"}
            
            # Store in vector database
            metadata = {
                "filename": filename,
                "file_type": file_type,
                "content_type": "image",
                "source": "uploaded_file"
            }
            
            vector_id = vector_store.add_item(cleaned_text, metadata)
            
            # Save processed data
            processed_data = {
                "vector_id": vector_id,
                "text": cleaned_text,
                "metadata": metadata
            }
            
            processed_file_path = os.path.join(PROCESSED_DIR, f"{os.path.splitext(filename)[0]}.json")
            with open(processed_file_path, 'w') as f:
                json.dump(processed_data, f)
            
            return {
                "status": "success",
                "message": "Image processed successfully",
                "extracted_text": cleaned_text[:100] + "..." if len(cleaned_text) > 100 else cleaned_text,
                "vector_id": vector_id
            }
            
        except Exception as e:
            return {"error": f"Error processing image: {str(e)}"}
    
    def _clean_text(self, text: str) -> str:
        """Clean up extracted text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove non-printable characters
        text = re.sub(r'[^\x20-\x7E]', '', text)
        return text.strip()

# Create a singleton instance
content_processor = ContentProcessor()