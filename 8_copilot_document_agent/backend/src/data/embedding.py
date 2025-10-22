from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class DocumentEmbedding:
    """Representa um embedding com seus metadados associados."""
    vector: List[float]
    metadata: Dict[str, Any]