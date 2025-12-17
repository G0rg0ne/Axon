from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi import UploadFile, File, HTTPException
import os
from dotenv import load_dotenv
import fitz
import pymupdf4llm
from loguru import logger
from typing import List, Optional
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
    "PROD": "https://axon-agent.online"
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[map_app_mode[APP_MODE]],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HealthResponse(BaseModel):
    status: str
    message: str

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

# Step 1: Parse PDF Response
class ParsePDFResponse(BaseModel):
    markdown: str
    sections: List[dict]
    section_count: int

# Step 2: Chunk Sections Request/Response
class ChunkSectionsRequest(BaseModel):
    sections: List[dict]
    filename: str

class ChunkResponse(BaseModel):
    chunks: List[dict]
    chunk_count: int

# Step 3: Extract Graph Request/Response
class ExtractGraphRequest(BaseModel):
    chunks: List[dict]

class ExtractGraphResponse(BaseModel):
    graph: GraphResponse
    chunk_count: int

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(status="ok", message="Axon API is running")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", message="All systems operational")

@app.post("/parse-pdf", response_model=ParsePDFResponse)
async def parse_pdf(file: UploadFile = File(...)):
    """Step 1: Upload PDF and convert to markdown, extract sections"""
    logger.info(f"Parsing PDF: {file.filename}")
    
    try:
        pdf_bytes = await file.read()
        
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            md_text = pymupdf4llm.to_markdown(doc)

        if not md_text:
            raise ValueError("No text extracted from PDF")

        sections = extract_sections_from_markdown(md_text)
        logger.info(f"Extracted {len(sections)} sections from {file.filename}")
        
        return ParsePDFResponse(
            markdown=md_text,
            sections=sections,
            section_count=len(sections)
        )

    except Exception as e:
        logger.error(f"Error parsing {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chunk-sections", response_model=ChunkResponse)
async def chunk_sections(request: ChunkSectionsRequest):
    """Step 2: Semantic chunking of sections"""
    logger.info(f"Chunking {len(request.sections)} sections for {request.filename}")
    
    try:
        all_chunks = []
        
        for sec in request.sections:
            section_chunks = semantic_chunk_text(
                text=sec['text'], 
                filename=request.filename,
                section_name=sec['section']
            )
            all_chunks.extend(section_chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks")
        
        return ChunkResponse(
            chunks=all_chunks,
            chunk_count=len(all_chunks)
        )

    except Exception as e:
        logger.error(f"Error chunking sections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-graph", response_model=ExtractGraphResponse)
async def extract_graph(request: ExtractGraphRequest):
    """Step 3: Extract knowledge graph from chunks"""
    logger.info(f"Extracting graph from {len(request.chunks)} chunks")
    
    try:
        all_nodes = {}
        all_edges = []
        
        for chunk in request.chunks:
            graph = extract_graph_from_chunk(chunk['text'], chunk['metadata'])
            
            for node in graph.nodes:
                if node.id not in all_nodes:
                    all_nodes[node.id] = NodeResponse(
                        id=node.id,
                        label=node.label,
                        type=node.type,
                        properties=node.properties.model_dump() if node.properties else None
                    )
            
            for edge in graph.edges:
                edge_response = EdgeResponse(
                    source=edge.source,
                    target=edge.target,
                    relationship=edge.relationship,
                    properties=edge.properties.model_dump() if edge.properties else None
                )
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
        
        return ExtractGraphResponse(
            graph=merged_graph,
            chunk_count=len(request.chunks)
        )

    except Exception as e:
        logger.error(f"Error extracting graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))
