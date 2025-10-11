from typing import List, Tuple, Union
from datetime import datetime
import json
import numpy as np
from collections import defaultdict
from storage.sqlite_store import SQLiteStore
from pathlib import Path
from api.core.database import SessionLocal
from api.core.models import Centroid

class VectorStore:
    """
    Embedding storage abstraction.
    Can be implemented with FAISS, ChromaDB, Pinecone, etc.
    Here it's in-memory for prototype.
    """

    def __init__(self, mode: str = "sqlite"):
        self.mode = mode
        self.vectors: List[Tuple[List[float], dict]] = []
        self.sqlite = SQLiteStore() if mode == "sqlite" else None
        self.centroids_path = Path("data/centroids.json")

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

    def retrain_model_backup(self):
        """
        Recalcula os centroides (médias vetoriais) por classe com base no SQLite.
        """
        print(f"🧩 Modo atual do VectorStore: {self.mode}")
        print(f"🧩 SQLite instanciado: {self.sqlite is not None}")

        if self.mode == "sqlite":
            self.vectors = self.sqlite.load_all()
        
        if not self.vectors:
            raise ValueError("Nenhum vetor encontrado para re-treinamento.")

        grouped = defaultdict(list)
        for vector, metadata in self.vectors:
            label = metadata.get("class_label")
            if label:
                grouped[label].append(np.array(vector, dtype=float))

        centroids = {
            label: np.mean(vectors, axis=0).tolist()
            for label, vectors in grouped.items()
        }

        # Salva em arquivo JSON
        self.centroids_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.centroids_path, "w") as f:
            json.dump(centroids, f, indent=2)

        print(f"Re-treinamento completo — {len(centroids)} classes atualizadas.")
        return {"status": "success", "classes_updated": list(centroids.keys())}

    def retrain_model(self):
        """
        Recalcula os centroides por classe e salva no banco.
        """
        if self.mode == "sqlite":
            if not self.vectors:
                self.vectors = self.sqlite.load_all()
        
        if not self.vectors:
            raise ValueError("Nenhum vetor encontrado para re-treinamento.")
        
        # Agrupa embeddings por classe
        class_embeddings = defaultdict(list)
        for vec, meta in self.vectors:
            class_embeddings[meta["class_label"]].append(vec)
        
        centroids = {}
        for cls, vecs in class_embeddings.items():
            avg_vec = np.mean(vecs, axis=0).tolist()
            centroids[cls] = avg_vec

            # Salva no banco
            session = SessionLocal()
            try:
                centroid_row = session.query(Centroid).filter(Centroid.class_label == cls).first()
                if centroid_row:
                    centroid_row.vector = avg_vec
                    centroid_row.updated_at = datetime.utcnow().timestamp()
                else:
                    centroid_row = Centroid(
                        class_label=cls,
                        vector=avg_vec,
                        updated_at=datetime.utcnow().timestamp()
                    )
                    session.add(centroid_row)
                session.commit()
            finally:
                session.close()
        
        print(f"🎯 Re-treinamento concluído. Centroides atualizados: {list(centroids.keys())}")
        return centroids

    def load_centroids(self):
        """Carrega centroides salvos, se existirem."""
        if not self.centroids_path.exists():
            return {}
        with open(self.centroids_path, "r") as f:
            return json.load(f)

    def predict_class(self, query_embedding: List[float], top_k: int = 5):
        """
        Predicts the most likely class.
        Se centroides existem, usa eles. Caso contrário, usa o método antigo baseado em vizinhos.
        """
        centroids = self.load_centroids()
        if centroids:
            best_label, best_score = None, -1
            for label, centroid in centroids.items():
                score = self.cosine_similarity(query_embedding, centroid)
                if score > best_score:
                    best_label, best_score = label, score
            return best_label, best_score, [{"centroid": best_label, "score": best_score}]

        # fallback: comportamento original
        return self._predict_from_neighbors(query_embedding, top_k)

    def _predict_from_neighbors(self, query_embedding: List[float], top_k: int = 5):
        """Lógica original separada pra manter o código limpo"""
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

    def vectors_by_class(self, class_label: str):
            """
            Retorna a lista de vetores de uma determinada classe.
            """
            return [vec for vec, meta in self.vectors if meta.get("class_label") == class_label]