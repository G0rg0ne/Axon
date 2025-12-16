from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import UploadFile, File, HTTPException
import os
from dotenv import load_dotenv
import fitz
import io
import pymupdf4llm
from loguru import logger
from typing import List
from .chunk_builder import (
    semantic_chunk_text,
    extract_sections_from_markdown,
)
from .ontology import extract_graph_from_chunk

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
    chunks: List[dict]

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(status="ok", message="Axon API is running")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", message="All systems operational")

#@app.post("/extract-text", response_model=ExtractPDFResponse)
# async def extract_text(file: UploadFile = File(...)):
#     logger.info(f"Extracting text from {file.filename}")
#     try:
#         pdf_bytes = await file.read()
#         pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
#         num_pages = len(pdf_reader.pages)
#         text_content = []
#         for page_num, page in enumerate(pdf_reader.pages, 1):
#             page_text = page.extract_text()
#             if page_text:
#                 text_content.append(f"--- Page {page_num} ---\n{page_text}")
#         logger.info(f"Successfully extracted text from {file.filename}")

#         chunks = semantic_chunk_text(text="\n\n".join(text_content))
#         if not chunks:
#             raise HTTPException(status_code=400, detail="No chunks found")

#         return ExtractPDFResponse(text="\n\n".join(text_content), num_pages=num_pages)
#     except Exception as e:
#         logger.error(f"Error extracting text from {file.filename}: {e}")
#        raise HTTPException(status_code=400, detail="Invalid PDF file")

@app.post("/extract-text")
async def extract_text(file: UploadFile = File(...)):
    logger.info(f"Extracting text from {file.filename}")
    
    try:
        pdf_bytes = await file.read()
        
        # 1. Convert to Markdown
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            md_text = pymupdf4llm.to_markdown(doc)

        if not md_text:
            raise ValueError("No text extracted")

        # 2. FIRST SPLIT: Split by Markdown Headers (Structural)
        raw_sections = extract_sections_from_markdown(md_text)
        
        all_chunks = []
        
        # 3. SECOND SPLIT: Semantic Chunking per Section
        for sec in raw_sections:
            logger.info(f"Processing section: {sec['section']}")
            section_chunks = semantic_chunk_text(
                text=sec['text'], 
                filename=file.filename,
                section_name=sec['section']
            )
            all_chunks.extend(section_chunks)
        logger.info(f"Created {len(all_chunks)} chunks from {len(raw_sections)} sections")
        for chunk in all_chunks:
            graph = extract_graph_from_chunk(chunk['text'], chunk['metadata'])
            logger.info(f"Graph: {graph}")
        return ExtractPDFResponse(chunks=all_chunks)

    except Exception as e:
        logger.error(f"Error processing {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))