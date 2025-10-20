import faiss
import numpy as np
from typing import List

class FaissVectorStore:
    """Armazena embeddings no FAISS para recuperação posterior."""

    def __init__(self, embedding_dim: int = 1536):
        self.index = faiss.IndexFlatL2(embedding_dim)

    def add_embeddings(self, embeddings: List[List[float]]):
        np_embeddings = np.array(embeddings).astype("float32")
        self.index.add(np_embeddings)

    def search(self, query_vector: List[float], k: int = 5):
        np_query = np.array([query_vector]).astype("float32")
        distances, indices = self.index.search(np_query, k)
        return distances, indices
