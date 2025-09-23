from typing import Any
from .embedder import Embedder
from .vector_store import VectorStore
from .retriever import Retriever

class RAGPipeline:
    """
    Orquestra o fluxo RAG:
    1. Gera embedding da query
    2. Recupera documentos similares
    3. (Opcional) passa para LLM
    """

    def __init__(self, embedder: Embedder, store: VectorStore):
        self.embedder = embedder
        self.retriever = Retriever(store)

    def run(self, query: str, top_k: int = 5) -> Any:
        query_embedding = self.embedder.generate(query)
        results = self.retriever.retrieve(query_embedding, top_k=top_k)
        # TODO: integrar com LLM para gerar resposta final
        return results
