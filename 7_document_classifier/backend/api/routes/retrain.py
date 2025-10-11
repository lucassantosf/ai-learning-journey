from fastapi import APIRouter, HTTPException
from storage.sqlite_store import SQLiteStore
from agent.vector_store import VectorStore  

router = APIRouter()

@router.post("/retrain")
def retrain_model():
    try:
        vector_store = VectorStore()
        centroids = vector_store.retrain_model()

        # Calcula contagem de embeddings por classe
        counts = {cls: len(vector_store.vectors_by_class(cls)) for cls in centroids.keys()}

        return {
            "message": "Modelo re-treinado com sucesso!",
            "updated_classes": list(centroids.keys()),
            "embedding_counts": counts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
