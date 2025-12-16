from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Optional
from openai import OpenAI
from langfuse import Langfuse
import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Initialize Langfuse client
langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
)

# 1. Define allowed Node Types (Labels) - aligned with system prompt
EntityType = Literal[
    "method", "metric", "dataset", "concept", 
    "technology", "result", "problem"
]

# 2. Define allowed Edge Types (Relations) - aligned with system prompt
RelationType = Literal[
    "USES", "IMPROVES", "EVALUATES_ON", "ACHIEVES", 
    "ADDRESSES", "OUTPERFORMS", "EXTENDS", "REQUIRES",
    "COMBINES_WITH", "COMPARES_TO", "PART_OF", "INSPIRED_BY"
]

# 3. Node properties
class EntityProperties(BaseModel):
    section: Optional[str] = Field(None, description="Document section where entity was found")
    canonical_name: Optional[str] = Field(None, description="Standardized name for the entity")
    aliases: Optional[list[str]] = Field(default_factory=list, description="Alternative names for this entity")
    description: Optional[str] = Field(None, description="Brief context from the text")

# 4. The Data Structure for an Extracted Node
class Entity(BaseModel):
    id: str = Field(..., description="Unique identifier for the entity (lowercase, underscore-separated)")
    label: str = Field(..., description="Display name of the entity (e.g., 'ResNet-50', 'F1-Score')")
    type: EntityType = Field(..., description="The category of the entity")
    properties: EntityProperties = Field(default_factory=EntityProperties)

# 5. Edge properties
class RelationProperties(BaseModel):
    confidence: Optional[Literal["high", "medium", "low"]] = Field(None, description="Confidence level of the relationship")
    context: Optional[str] = Field(None, description="Original sentence or phrase supporting this relationship")
    section: Optional[str] = Field(None, description="Document section where relationship was found")
    quantitative_detail: Optional[str] = Field(None, description="Any numbers/metrics if applicable")

# 6. The Data Structure for an Extracted Edge
class Relation(BaseModel):
    source: str = Field(..., description="ID of the source entity")
    target: str = Field(..., description="ID of the target entity")
    relationship: RelationType = Field(..., description="The relationship type between source and target")
    properties: RelationProperties = Field(default_factory=RelationProperties)

# 7. The Container for the whole extraction
class KnowledgeGraphExtraction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    nodes: list[Entity] = Field(default_factory=list, alias="entities")
    edges: list[Relation] = Field(default_factory=list, alias="relations")

def extract_graph_from_chunk(chunk_text: str, chunk_metadata: dict) -> KnowledgeGraphExtraction:
    """
    Uses the LLM to extract entities and relations from a single text chunk.
    """
    
    # Fetch the system prompt from Langfuse
    prompt = langfuse.get_prompt("graph_maker")
    system_prompt = prompt.compile(
        section=chunk_metadata.get('section', 'Unknown'),
        chunk_text=chunk_text
    )
    # Use OpenAI's structured output (beta) to enforce Pydantic schema
    try:
        completion = client.beta.chat.completions.parse(
            model=MODEL,
            temperature=0.1,
            messages=[
                {"role": "system", "content": system_prompt},
            ],
            response_format=KnowledgeGraphExtraction
        )
        return completion.choices[0].message.parsed
    except Exception as e:
        print(f"Extraction failed: {e}")
        return KnowledgeGraphExtraction(nodes=[], edges=[])