from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

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

import os
from fastapi.responses import JSONResponse, FileResponse

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), file_type: str = Form("document")):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename, "file_type": file_type}

@app.get("/files/")
def list_files():
    files = os.listdir(UPLOAD_DIR)
    return JSONResponse(content={"files": files})

@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return JSONResponse(content={"error": "File not found"}, status_code=404)

@app.post("/query/")
async def query(question: str = Form(...)):
    # Simple gold trading knowledge base
    knowledge_base = {
        "gold price": "Gold prices fluctuate based on market conditions, economic indicators, and geopolitical events. As of the last update, gold was trading around $2,000 per ounce, but this can change rapidly.",
        "investment": "Gold is considered a safe-haven asset that can help diversify investment portfolios and hedge against inflation and currency devaluation.",
        "trading hours": "Gold trades nearly 24 hours a day on markets around the world, with the main trading centers being London, New York, and Shanghai.",
        "factors": "Key factors affecting gold prices include interest rates, inflation, currency values (especially USD), central bank policies, and global economic uncertainty.",
        "etf": "Gold ETFs (Exchange-Traded Funds) allow investors to gain exposure to gold prices without physically owning gold. Popular options include GLD and IAU.",
        "physical gold": "Physical gold can be purchased as coins, bars, or jewelry. When buying physical gold, consider purity (measured in karats), premium over spot price, and storage costs.",
        "technical analysis": "Common technical indicators for gold trading include moving averages, RSI (Relative Strength Index), MACD (Moving Average Convergence Divergence), and Fibonacci retracement levels.",
        "seasonal patterns": "Gold often shows seasonal patterns, with prices typically stronger during certain months like September and weaker during others."
    }
    
    # Simple response generation based on keywords in the question
    question = question.lower()
    response = "I don't have specific information about that aspect of gold trading. Consider asking about gold prices, investment strategies, trading hours, price factors, ETFs, physical gold, technical analysis, or seasonal patterns."
    
    for keyword, answer in knowledge_base.items():
        if keyword in question:
            response = answer
            break
    
    return {"answer": response}
