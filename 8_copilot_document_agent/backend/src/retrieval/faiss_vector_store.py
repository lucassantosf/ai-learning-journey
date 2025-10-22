import faiss
import numpy as np
import os
from typing import List, Tuple


class FaissVectorStore:
    """
    Classe responsável por armazenar, buscar e persistir embeddings utilizando FAISS.
    """

    def __init__(self, path: str = "faiss_index.bin", embedding_dim: int = 1536):
        self.path = path
        self.embedding_dim = embedding_dim

        # Se o arquivo já existe, carrega; senão, cria um novo índice
        if os.path.exists(self.path):
            self.index = faiss.read_index(self.path)
        else:
            self.index = faiss.IndexFlatL2(self.embedding_dim)

    def add_embeddings(self, vectors: List[List[float]]):
        """Adiciona embeddings ao índice."""
        np_vectors = np.array(vectors).astype("float32")
        self.index.add(np_vectors)

    def count(self) -> int:
        """Retorna o número de vetores armazenados."""
        return self.index.ntotal

    def search(self, query_vector: List[float], k: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """Realiza busca no índice FAISS."""
        np_query = np.array([query_vector]).astype("float32")
        distances, indices = self.index.search(np_query, k)
        return distances, indices

    def save(self):
        """Salva o índice FAISS no caminho especificado."""
        faiss.write_index(self.index, self.path)

    def load(self):
        """Carrega o índice FAISS do disco."""
        if os.path.exists(self.path):
            self.index = faiss.read_index(self.path)
        else:
            raise FileNotFoundError(f"O índice {self.path} não foi encontrado.")

    def reconstruct(self, id: int) -> np.ndarray:
        """Reconstrói o vetor armazenado em um ID específico."""
        return self.index.reconstruct(id)

    def get_stats(self) -> dict:
        """Retorna informações básicas do índice FAISS."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.embedding_dim
        }