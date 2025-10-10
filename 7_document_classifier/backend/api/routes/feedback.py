from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agent.document_agent import DocumentAgent  # opcional, se já implementado
from agent.vector_store import VectorStore  # opcional, se já implementado

router = APIRouter()

class FeedbackPayload(BaseModel):
    document_id: int
    correct_class: str
    notes: str | None = None
    update_vector_store: bool = True

@router.post("/feedback")
def feedback_loop(payload: FeedbackPayload):
    """
    Endpoint de feedback loop.
    Permite corrigir a classificação de um documento e atualizar o VectorStore.
    """
    agent = DocumentAgent()      # usa SQLiteStore já configurado
    vector_store = VectorStore() # inicializa VectorStore

    # 1️⃣ Atualiza classificação no banco
    result = agent.update_classification(
        document_id=payload.document_id,
        correct_class=payload.correct_class,
        notes=payload.notes
    )
    if result["status"] != "success":
        raise HTTPException(status_code=404, detail="Documento não encontrado")

    # 2️⃣ Recupera o documento com embedding (retorna dict)
    doc = agent.get_document(payload.document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado após atualização")

    # 3️⃣ Atualiza VectorStore com embedding corrigido
    if payload.update_vector_store and doc.get("embedding"):
        vector_store.add(doc["embedding"], {
            "doc_id": doc["id"],
            "class_label": payload.correct_class
        })

    return {
        "status": "ok",
        "document_id": payload.document_id,
        "correct_class": payload.correct_class
    }