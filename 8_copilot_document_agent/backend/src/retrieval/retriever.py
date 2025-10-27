import numpy as np
from typing import List, Dict, Any, Optional
from src.retrieval.faiss_vector_store import FaissVectorStore
from src.core.logger import log_info

class Retriever:
    """
    Recuperador de trechos mais relevantes usando FAISS com similaridade de cosseno real.
    Base para o pipeline RAG.
    """

    def __init__(
        self,
        vector_store: FaissVectorStore,
        embedding_model: Any,
        default_k: int = 5,
        normalize_embeddings: bool = True
    ):
        """
        :param vector_store: instância de FaissVectorStore já carregada
        :param embedding_model: modelo com método embed_text(text) -> List[float]
        :param default_k: número padrão de resultados a retornar
        :param normalize_embeddings: se True, normaliza vetores para cálculo de cosine similarity
        """
        self.vector_store = vector_store
        self.embedding_model = embedding_model
        self.default_k = default_k
        self.normalize = normalize_embeddings

    def _validate_index(self):
        """Garante que o índice FAISS não está vazio."""
        stats = self.vector_store.get_stats()
        if stats["total_vectors"] == 0:
            raise ValueError("O índice FAISS está vazio. Adicione embeddings antes de realizar buscas.")

    def _normalize_vector(self, v: np.ndarray) -> np.ndarray:
        """Normaliza um vetor para norma unitária (usado para cosine similarity)."""
        norm = np.linalg.norm(v)
        if norm == 0:
            raise ValueError("Vetor de embedding com norma zero.")
        return v / norm

    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Busca os chunks mais similares à query usando similaridade de cosseno.

        :param query: texto da consulta
        :param top_k: número de resultados (default = self.default_k)
        :return: lista de dicionários [{ "text": ..., "score": ..., "metadata": {...} }]
        """
        self._validate_index()
        k = top_k or self.default_k

        # 1️⃣ Gera embedding da query
        try:
            query_vector = self.embedding_model.embed_text(query)
            query_vector = np.array(query_vector, dtype="float32")
        except Exception as e:
            raise ValueError(f"Falha ao gerar embedding da query: {e}")

        if query_vector.shape[0] != self.vector_store.embedding_dim:
            raise ValueError(
                f"Dimensão do embedding da query ({query_vector.shape[0]}) "
                f"não corresponde à do índice ({self.vector_store.embedding_dim})"
            )

        # 2️⃣ Normaliza vetores (para cosine similarity)
        if self.normalize:
            query_vector = self._normalize_vector(query_vector)

        # O FAISS armazenou embeddings não normalizados?
        # Se sim, normalizamos temporariamente antes da busca
        index_copy = self.vector_store.index
        if self.normalize:
            # Copia todos os vetores atuais do índice
            xb = self.vector_store.index.reconstruct_n(0, self.vector_store.index.ntotal)
            xb = np.array([self._normalize_vector(v) for v in xb], dtype="float32")

            # cria índice temporário para busca
            import faiss
            temp_index = faiss.IndexFlatIP(self.vector_store.embedding_dim)
            temp_index.add(xb)
            distances, indices = temp_index.search(
                np.array([query_vector], dtype="float32"), k
            )
        else:
            distances, indices = index_copy.search(
                np.array([query_vector], dtype="float32"), k
            )

        # 3️⃣ Monta resultados
        distances = distances.flatten()
        indices = indices.flatten()

        results: List[Dict[str, Any]] = []
        for score, idx in zip(distances, indices):
            if idx == -1 or idx >= len(self.vector_store.metadata):
                continue

            meta = self.vector_store.metadata[idx] or {}
            text = meta.get("text") or meta.get("content") or "<sem_texto>"

            results.append({
                "text": text,
                "score": float(score),
                "metadata": meta
            })

        log_info(f"🔍 Consulta '{query}' retornou {len(results)} resultados (k={k})")
        return results
