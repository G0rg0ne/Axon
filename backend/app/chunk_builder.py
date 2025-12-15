from llama_index.core import Document
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize embedding model and semantic splitter
embed_model = OpenAIEmbedding(
    model="text-embedding-3-small",
    api_key=OPENAI_API_KEY
)
semantic_splitter = SemanticSplitterNodeParser(
    buffer_size=1,              # Sentences to group for comparison
    breakpoint_percentile_threshold=95,  # Higher = fewer splits
    embed_model=embed_model
)

def semantic_chunk_text(text: str) -> list[dict]:
    """
    Split text using LlamaIndex SemanticSplitter.
    Groups sentences by semantic similarity.
    """
    # Create a LlamaIndex Document from the text
    document = Document(text=text)
    
    # Parse into semantically coherent nodes
    nodes = semantic_splitter.get_nodes_from_documents([document])
    
    chunks = []
    for i, node in enumerate(nodes):
        chunks.append({
            "id": i,
            "text": node.get_content(),
            "char_count": len(node.get_content()),
            "metadata": node.metadata
        })
    
    return chunks