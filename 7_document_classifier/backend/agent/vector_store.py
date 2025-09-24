from typing import List, Tuple
import numpy as np

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
        Espera um dict com 'embedding' e metadados adicionais.
        """
        self.vectors.append((embedding, metadata))

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calcula a similaridade cosseno entre dois vetores.
        """
        a = np.array(vec1)
        b = np.array(vec2)
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[dict, float]]:
        """
        Retorna os top_k embeddings mais similares ao query_embedding.
        """
        similarities = []

        for vec, meta in self.vectors:
            sim = self.cosine_similarity(query_embedding, vec)
            similarities.append((meta, sim))

        # Ordena do mais similar para o menos similar
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
