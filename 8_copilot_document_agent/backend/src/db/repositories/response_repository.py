# src/db/repositories/response_repository.py

from sqlalchemy.orm import Session
from typing import Optional, List
from src.db import models


class ResponseRepository:
    """
    Repositório responsável por armazenar e recuperar respostas geradas pelo agente.
    Pode ser associado a uma consulta (query_id).
    """

    def __init__(self, db: Session):
        self.db = db

    # ======================================================
    # ➕ Inserção
    # ======================================================

    def add_response(
        self,
        query_id: Optional[int],
        answer: str,
        model_name: str,
        confidence: Optional[float] = None,
        feedback: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> models.AgentResponse:
        """Registra uma nova resposta do agente."""
        response = models.AgentResponse(
            query_id=query_id,
            answer=answer,
            model_name=model_name,
            confidence=confidence,
            feedback=feedback,
            metadata=metadata or {},
        )
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)
        return response

    # ======================================================
    # 🔍 Consulta
    # ======================================================

    def get_by_id(self, response_id: int) -> Optional[models.AgentResponse]:
        """Recupera uma resposta específica."""
        return self.db.query(models.AgentResponse).filter(models.AgentResponse.id == response_id).first()

    def list_by_query(self, query_id: int) -> List[models.AgentResponse]:
        """Lista todas as respostas associadas a uma consulta."""
        return (
            self.db.query(models.AgentResponse)
            .filter(models.AgentResponse.query_id == query_id)
            .order_by(models.AgentResponse.created_at.desc())
            .all()
        )

    def list_recent(self, limit: int = 20) -> List[models.AgentResponse]:
        """Lista as respostas mais recentes geradas pelo agente."""
        return (
            self.db.query(models.AgentResponse)
            .order_by(models.AgentResponse.created_at.desc())
            .limit(limit)
            .all()
        )

    # ======================================================
    # 🧾 Atualização
    # ======================================================

    def update_feedback(self, response_id: int, feedback: str) -> Optional[models.AgentResponse]:
        """Adiciona ou atualiza o feedback do usuário sobre uma resposta."""
        response = self.get_by_id(response_id)
        if not response:
            return None
        response.feedback = feedback
        self.db.commit()
        self.db.refresh(response)
        return response

    # ======================================================
    # ❌ Exclusão
    # ======================================================

    def delete_by_id(self, response_id: int) -> bool:
        """Remove uma resposta específica."""
        response = self.get_by_id(response_id)
        if not response:
            return False
        self.db.delete(response)
        self.db.commit()
        return True

    def clear_all(self):
        """Remove todas as respostas armazenadas."""
        self.db.query(models.AgentResponse).delete()
        self.db.commit()