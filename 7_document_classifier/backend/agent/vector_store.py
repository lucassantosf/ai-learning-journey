from typing import List, Tuple, Union
import numpy as np
from collections import defaultdict


class VectorStore:
    """
    Abstração do armazenamento de embeddings.
    Pode ser implementado com FAISS, ChromaDB, Pinecone, etc.
    Aqui é em memória para protótipo.
    """

    def __init__(self):
        self.vectors: List[Tuple[List[float], dict]] = []  # Lista de tuplas (embedding, metadata)

    def add(self, embedding: Union[List[float], np.ndarray, float], metadata: dict):
        """
        Adiciona um embedding ao armazenamento.
        Aceita list, numpy.ndarray ou até float (neste caso vira [float]).
        """
        if isinstance(embedding, float):  # se vier número único por engano
            embedding = [embedding]
        elif isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        elif not isinstance(embedding, list):
            raise TypeError(f"Embedding inválido: {type(embedding)}")

        self.vectors.append((embedding, metadata))

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        a = np.array(vec1, dtype=float)
        b = np.array(vec2, dtype=float)
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[dict, float]]:
        """
        Retorna os top_k embeddings mais similares ao query_embedding.
        """
        similarities: List[Tuple[dict, float]] = []

        for vec, meta in self.vectors:
            sim = self.cosine_similarity(query_embedding, vec)
            similarities.append((meta, sim))

        # Ordena do mais similar para o menos similar
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def predict_class(self, query_embedding: List[float], top_k: int = 5):
        """
        Prediz a classe mais provável com base na média das similaridades
        dos top_k resultados mais próximos.
        """
        results = self.search(query_embedding, top_k=top_k)

        if not results:
            return None, 0.0, []

        class_scores = defaultdict(list)
        for meta, score in results:
            if "class_label" not in meta:
                raise KeyError(f"Metadata sem 'class_label': {meta}")
            class_scores[meta["class_label"]].append(score)

        avg_scores = {cls: sum(scores) / len(scores) for cls, scores in class_scores.items()}
        predicted_class = max(avg_scores, key=avg_scores.get)
        confidence = avg_scores[predicted_class]

        return predicted_class, confidence, results