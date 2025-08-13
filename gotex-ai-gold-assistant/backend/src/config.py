import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
PINCONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINCONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# AI Provider Configuration
DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "openai")  # openai, deepseek, or auto
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# Vector Database Configuration
VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME", "gotex-knowledge")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 1536))

# File Storage
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.abspath(os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploaded_files")))
PROCESSED_DIR = os.path.abspath(os.getenv("PROCESSED_DIR", os.path.join(BASE_DIR, "processed_files")))

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
print(f"Upload directory: {UPLOAD_DIR}")
print(f"Processed directory: {PROCESSED_DIR}")

# Application Settings
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 8000))