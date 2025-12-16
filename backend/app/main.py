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
from typing import List, Optional
from .chunk_builder import (
    semantic_chunk_text,
    extract_sections_from_markdown,
)
from .ontology import extract_graph_from_chunk, KnowledgeGraphExtraction

load_dotenv()
APP_MODE = os.getenv("APP_MODE","DEV")

app = FastAPI(
    title="Axon API",
    description="Backend API for Axon application",
    version="1.0.0"
)

map_app_mode = {
    "DEV": "http://localhost:8501",
    "PROD": "https://axon-agent.online"
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

# Response models for graph extraction
class NodeResponse(BaseModel):
    id: str
    label: str
    type: str
    properties: Optional[dict] = None

class EdgeResponse(BaseModel):
    source: str
    target: str
    relationship: str
    properties: Optional[dict] = None

class GraphResponse(BaseModel):
    nodes: List[NodeResponse]
    edges: List[EdgeResponse]

class ExtractPDFResponse(BaseModel):
    graph: GraphResponse
    chunk_count: int

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(status="ok", message="Axon API is running")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", message="All systems operational")

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

        # Extract knowledge graphs from each chunk and merge them
        all_nodes = {}  # Use dict to deduplicate by id
        all_edges = []
        
        for chunk in all_chunks:
            graph = extract_graph_from_chunk(chunk['text'], chunk['metadata'])
            
            # Merge nodes (deduplicate by id)
            for node in graph.nodes:
                if node.id not in all_nodes:
                    all_nodes[node.id] = NodeResponse(
                        id=node.id,
                        label=node.label,
                        type=node.type,
                        properties=node.properties.model_dump() if node.properties else None
                    )
            
            # Add edges (avoid exact duplicates)
            for edge in graph.edges:
                edge_response = EdgeResponse(
                    source=edge.source,
                    target=edge.target,
                    relationship=edge.relationship,
                    properties=edge.properties.model_dump() if edge.properties else None
                )
                # Check for duplicate edges
                is_duplicate = any(
                    e.source == edge_response.source and 
                    e.target == edge_response.target and 
                    e.relationship == edge_response.relationship 
                    for e in all_edges
                )
                if not is_duplicate:
                    all_edges.append(edge_response)
        
        merged_graph = GraphResponse(
            nodes=list(all_nodes.values()),
            edges=all_edges
        )
        
        logger.info(f"Extracted {len(merged_graph.nodes)} nodes and {len(merged_graph.edges)} edges")
        
        return ExtractPDFResponse(graph=merged_graph, chunk_count=len(all_chunks))

    except Exception as e:
        logger.error(f"Error processing {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))