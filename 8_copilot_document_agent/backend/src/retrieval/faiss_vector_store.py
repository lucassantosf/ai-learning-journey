
import faiss
import numpy as np
from typing import List, Optional
from src.core.logger import log_info

class FaissVectorStore:
    """FAISS index simples com armazenamento de metadados."""

    def __init__(self, embedding_dim: int = 1536):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.metadata: List[dict] = []

    def add_embeddings(self, vectors: List[List[float]], metadatas: Optional[List[dict]] = None):
        if not vectors:
            return
        array = np.array(vectors, dtype="float32")
        
        if len(array.shape) != 2:
            log_info(f"❌ Vetores malformados: shape={array.shape}. Verifique dimensões inconsistentes.")
            raise ValueError(f"Vetores malformados: shape={array.shape}")

        if array.shape[1] != self.embedding_dim:
            log_info(f"❌ Dimensão incorreta dos embeddings! Esperado {self.embedding_dim}, recebido {array.shape[1]}")
            raise ValueError(f"Dimensão incorreta dos embeddings! Esperado {self.embedding_dim}, recebido {array.shape[1]}")

        self.index.add(array)
        if metadatas:
            self.metadata.extend(metadatas)
        log_info(f"✅ Adicionados {len(vectors)} vetores ao FAISS.")

    def search(self, query_vector: List[float], top_k: int = 5):
        D, I = self.index.search(np.array([query_vector], dtype="float32"), top_k)
        results = []
        for i, score in zip(I[0], D[0]):
            meta = self.metadata[i] if i < len(self.metadata) else {}
            results.append({"score": float(score), "metadata": meta})
        return results
