from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Document:
    id: str
    name: str
    type: str
    content: Optional[str] = None
    metadata: Optional[dict] = None

@dataclass
class Chunk:
    document_id: str
    text: str
    position: int

@dataclass
class EmbeddingVector:
    document_id: str
    text: str
    embedding: List[float]