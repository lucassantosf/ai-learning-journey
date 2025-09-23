from typing import List, Tuple
from .vector_store import VectorStore

class Retriever:
    """
    Responsável por buscar documentos similares no VectorStore.
    """

    def __init__(self, store: VectorStore):
        self.store = store

    def retrieve(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[dict, float]]:
        return self.store.search(query_embedding, top_k=top_k)
