# src/db/repositories/query_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from src.db import models


class QueryRepository:
    """
    Repositório para consultas feitas ao sistema (perguntas e respostas).
    Cada consulta pode estar associada a um ou mais documentos e chunks.
    """

    def __init__(self, db: Session):
        self.db = db

    # ======================================================
    # ➕ Inserção
    # ======================================================

    def add_query(
        self,
        question: str,
        answer: str,
        used_chunks: Optional[List[int]] = None,
        metadata: Optional[dict] = None,
    ) -> models.Query:
        """
        Registra uma nova consulta no histórico.
        """
        query = models.Query(question=question)
        self.db.add(query)
        self.db.commit()
        self.db.refresh(query)

        # Adiciona a resposta associada à consulta
        response = models.Response(
            query_id=query.id, 
            answer=answer, 
            data=metadata or {}
        )
        self.db.add(response)
        self.db.commit()

        return query

    # ======================================================
    # 🔍 Consulta
    # ======================================================

    def get_by_id(self, query_id: int) -> Optional[models.Query]:
        """Busca uma consulta específica pelo ID."""
        return self.db.query(models.Query).filter(models.Query.id == query_id).first()

    def list_recent(self, limit: int = 20) -> List[models.Query]:
        """Lista as consultas mais recentes."""
        return (
            self.db.query(models.Query)
            .order_by(models.Query.created_at.desc())
            .limit(limit)
            .all()
        )

    def search_by_keyword(self, keyword: str, limit: int = 20) -> List[models.Query]:
        """Procura consultas que contenham uma palavra-chave na pergunta."""
        return (
            self.db.query(models.Query)
            .filter(models.Query.question.ilike(f"%{keyword}%"))
            .limit(limit)
            .all()
        )

    # ======================================================
    # ❌ Exclusão
    # ======================================================

    def delete_by_id(self, query_id: int) -> bool:
        """Remove uma consulta específica."""
        query = self.get_by_id(query_id)
        if not query:
            return False
        self.db.delete(query)
        self.db.commit()
        return True

    def clear_history(self):
        """Remove todo o histórico de consultas."""
        self.db.query(models.Query).delete()
        self.db.commit()
