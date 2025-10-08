from typing import List, Tuple, Union
import numpy as np
from collections import defaultdict
from storage.sqlite_store import SQLiteStore

class VectorStore:
    """
    Embedding storage abstraction.
    Can be implemented with FAISS, ChromaDB, Pinecone, etc.
    Here it's in-memory for prototype.
    """

    def __init__(self, mode: str = "json"):
        self.mode = mode
        self.vectors: List[Tuple[List[float], dict]] = []
        self.sqlite = SQLiteStore() if mode == "sqlite" else None

        if self.mode == "sqlite":
            print("💾 VectorStore in SQLite mode — lazy loading enabled")
        else:
            print("📄 VectorStore in JSON/in-memory mode")

    def add(self, embedding: Union[List[float], np.ndarray, float], metadata: dict):
        """
        Adds an embedding to storage.
        Accepts list, numpy.ndarray or even float (in this case becomes [float]).
        """
        if isinstance(embedding, float):  # if single number comes by mistake
            embedding = [embedding]
        elif isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()
        elif not isinstance(embedding, list):
            raise TypeError(f"Invalid embedding: {type(embedding)}")

        if self.mode == "json":
            self.vectors.append((embedding, metadata))
        elif self.mode == "sqlite":
            self.sqlite.save_vector(embedding, metadata)

    def load_from_sqlite(self):
        if self.sqlite:
            self.vectors = self.sqlite.load_all()
            print(f"📚 Loaded {len(self.vectors)} vectors from SQLite")

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        a, b = np.array(vec1, dtype=float), np.array(vec2, dtype=float)
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[dict, float]]:
        if self.mode == "sqlite" and not self.vectors:
            self.load_from_sqlite()

        similarities = []
        for vec, meta in self.vectors:
            sim = self.cosine_similarity(query_embedding, vec)
            similarities.append((meta, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def predict_class(self, query_embedding: List[float], top_k: int = 5):
        """
        Predicts the most likely class based on the average similarities
        of the top_k closest results.
        """
        results = self.search(query_embedding, top_k=top_k)

        if not results:
            return None, 0.0, []

        class_scores = defaultdict(list)
        for meta, score in results:
            if "class_label" not in meta:
                raise KeyError(f"Metadata without 'class_label': {meta}")
            class_scores[meta["class_label"]].append(score)

        avg_scores = {cls: sum(scores) / len(scores) for cls, scores in class_scores.items()}
        predicted_class = max(avg_scores, key=avg_scores.get)
        confidence = avg_scores[predicted_class]

        return predicted_class, confidence, results
