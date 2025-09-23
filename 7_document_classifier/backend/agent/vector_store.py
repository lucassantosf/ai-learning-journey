from typing import List, Tuple

class VectorStore:
    """
    Abstração do armazenamento de embeddings.
    Pode ser implementado com FAISS, ChromaDB, Pinecone, etc.
    """

    def __init__(self):
        self.vectors = []  # Lista de tuplas (embedding, metadata)

    def add(self, embedding: List[float], metadata: dict):
        """
        Adiciona um embedding ao repositório.
        """
        self.vectors.append((embedding, metadata))

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[dict, float]]:
        """
        Retorna os top_k embeddings mais similares.
        (Por enquanto, retorna vazio ou tudo fake)
        """
        # TODO: implementar cálculo de similaridade real
        return []
