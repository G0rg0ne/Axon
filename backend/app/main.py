from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import UploadFile, File
import os
from dotenv import load_dotenv
import PyPDF2
import io
from loguru import logger

from .chunk_builder import (
    semantic_chunk_text,
)

load_dotenv()
APP_MODE = os.getenv("APP_MODE","DEV")

app = FastAPI(
    title="Axon API",
    description="Backend API for Axon application",
    version="1.0.0"
)

map_app_mode = {
    "DEV": "http://localhost:8501",
    "PROD": "https://gorgone.app"
}
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[map_app_mode[APP_MODE]],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    message: str

class ExtractPDFResponse(BaseModel):
    text: str
    num_pages: int

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(status="ok", message="Axon API is running")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", message="All systems operational")

@app.post("/extract-text", response_model=ExtractPDFResponse)
async def extract_text(file: UploadFile = File(...)):
    logger.info(f"Extracting text from {file.filename}")
    pdf_bytes = await file.read()
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    num_pages = len(pdf_reader.pages)
    text_content = []
    for page_num, page in enumerate(pdf_reader.pages, 1):
        page_text = page.extract_text()
        if page_text:
            text_content.append(f"--- Page {page_num} ---\n{page_text}")
    logger.info(f"Successfully extracted text from {file.filename}")
    chunks = semantic_chunk_text(text="\n\n".join(text_content))
    logger.debug(f"Chunks: {chunks}")
    return ExtractPDFResponse(text="\n\n".join(text_content), num_pages=num_pages)