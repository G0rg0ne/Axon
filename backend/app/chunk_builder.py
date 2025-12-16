from llama_index.core import Document
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
import os
import re
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize embedding model and semantic splitter
embed_model = OpenAIEmbedding(
    model="text-embedding-3-large", # Changed from 'small'
    dimensions=3072,                # Explicitly set higher dimensions
    api_key=OPENAI_API_KEY
)
semantic_splitter = SemanticSplitterNodeParser(
    buffer_size=1,              # Sentences to group for comparison
    breakpoint_percentile_threshold=95,  # Higher = fewer splits
    embed_model=embed_model
)


def extract_sections_from_markdown(markdown_text: str) -> list[dict]:
    """
    Splits a markdown document into sections based on headers.
    Handles:
      - Markdown headers: # Title, ## Section, ### Subsection
      - Bold-only headers: **Introduction** (common in PDF conversions)
      - Multi-bold headers: **3** **Model Architecture** (numbered sections)
    Returns a list of dicts: [{'section': 'Introduction', 'text': '...'}, ...]
    """
    # Pattern 1: Standard markdown headers (# ## ###)
    # Pattern 2: Bold text on its own line - handles both single and multi-bold patterns
    #   - Single: **Introduction**
    #   - Multi:  **3** **Model Architecture** or **3.1** **Encoder Stacks**
    header_pattern = re.compile(
        r'^(?:'
        r'(#{1,3})\s+(.+)'                              # Group 1,2: Markdown headers (# Title)
        r'|'
        r'(\*\*[^*\n]+\*\*(?:\s+\*\*[^*\n]+\*\*)*)\s*$' # Group 3: One or more bold blocks
        r')',
        re.MULTILINE
    )
    
    matches = list(header_pattern.finditer(markdown_text))
    sections = []
    
    # 1. Handle text BEFORE the first header (often the Abstract or Title info)
    if matches and matches[0].start() > 0:
        preamble_text = markdown_text[:matches[0].start()].strip()
        if preamble_text:
            sections.append({
                "section": "Abstract_or_Preamble", 
                "text": preamble_text
            })
    
    # 2. Iterate through matches to get text between headers
    for i, match in enumerate(matches):
        # Extract section title from either pattern
        if match.group(2):  # Markdown header (# Title)
            section_title = match.group(2).strip()
            # Clean up bold markers if present in markdown header
            section_title = re.sub(r'\*\*([^*]+)\*\*', r'\1', section_title)
        else:  # Bold header(s) - could be **Title** or **3** **Title**
            raw_title = match.group(3).strip()
            # Remove all ** markers and clean up whitespace
            section_title = re.sub(r'\*\*', '', raw_title).strip()
            # Normalize multiple spaces to single space
            section_title = re.sub(r'\s+', ' ', section_title)
        
        start_index = match.end()  # Start after the header
        
        # End at the start of the next header, or end of document
        if i + 1 < len(matches):
            end_index = matches[i + 1].start()
        else:
            end_index = len(markdown_text)
            
        section_content = markdown_text[start_index:end_index].strip()
        
        # Filter out empty sections or just newlines
        if section_content:
            sections.append({
                "section": section_title,
                "text": section_content
            })
            
    # Fallback: If no headers found, treat whole text as one section
    if not sections and markdown_text.strip():
        sections.append({"section": "Full_Document", "text": markdown_text})
        
    return sections


def semantic_chunk_text(text: str, filename: str, section_name: str = "Uncategorized") -> list[dict]:
    """
    Split text ensuring metadata is preserved for Graph RAG.
    """
    if not text or not text.strip():
        return []

    # 1. Inject Metadata HERE so it propagates to the nodes
    # This is crucial for Graph RAG (identifying which paper/section a node belongs to)
    initial_metadata = {
        "filename": filename,
        "section": section_name,
        "category": "scientific_paper"
    }

    try:    
        document = Document(text=text, metadata=initial_metadata)
        
        # 2. Get Nodes
        nodes = semantic_splitter.get_nodes_from_documents([document])
        
        chunks = []
        for node in nodes:
            chunks.append({
                "id": node.id_,
                "text": node.get_content(),
                "char_count": len(node.get_content()),
                "metadata": node.metadata, 
            })
        return chunks

    except Exception as e:
        logger.error(f"Error chunking {filename}: {e}")
        return []