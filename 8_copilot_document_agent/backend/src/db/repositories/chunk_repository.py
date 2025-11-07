# src/db/repositories/chunk_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from src.db import models


class ChunkRepository:
    """
    Repositório responsável por manipular os pedaços (chunks) de texto extraídos de documentos.
    """

    def __init__(self, db: Session):
        self.db = db

    # ======================================================
    # ➕ Inserção
    # ======================================================

    def add_chunk(
        self,
        document_id: int,
        content: str,
        order: int,
        metadata: Optional[dict] = None,
    ) -> models.Chunk:
        """Adiciona um novo chunk vinculado a um documento."""
        chunk = models.Chunk(
            document_id=document_id,
            content=content,
            chunk_index=order,
            metadata=metadata or {},
        )
        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk

    def add_many(self, document_id: int, chunks: List[str]) -> List[models.Chunk]:
        """Adiciona vários chunks de uma vez, preservando a ordem."""
        created_chunks = []
        for idx, content in enumerate(chunks):
            chunk = models.Chunk(
                document_id=document_id,
                content=content,
                chunk_index=idx,
                metadata={},
            )
            self.db.add(chunk)
            created_chunks.append(chunk)
        self.db.commit()
        return created_chunks

    # ======================================================
    # 🔍 Consulta
    # ======================================================

    def get_by_id(self, chunk_id: int) -> Optional[models.Chunk]:
        """Busca um chunk pelo seu ID."""
        return self.db.query(models.Chunk).filter(models.Chunk.id == chunk_id).first()

    def list_by_document(self, document_id: int) -> List[models.Chunk]:
        """Lista todos os chunks vinculados a um documento."""
        return (
            self.db.query(models.Chunk)
            .filter(models.Chunk.document_id == document_id)
            .order_by(models.Chunk.order.asc())
            .all()
        )

    def search(self, term: str, limit: int = 10) -> List[models.Chunk]:
        """Busca chunks que contenham um termo específico."""
        return (
            self.db.query(models.Chunk)
            .filter(models.Chunk.content.ilike(f"%{term}%"))
            .limit(limit)
            .all()
        )

    # ======================================================
    # 🧾 Atualização
    # ======================================================

    def update_metadata(self, chunk_id: int, metadata: dict) -> Optional[models.Chunk]:
        """Atualiza o campo metadata de um chunk específico."""
        chunk = self.get_by_id(chunk_id)
        if not chunk:
            return None
        chunk.metadata = metadata
        self.db.commit()
        self.db.refresh(chunk)
        return chunk

    # ======================================================
    # ❌ Exclusão
    # ======================================================

    def delete_by_id(self, chunk_id: int) -> bool:
        """Remove um chunk específico."""
        chunk = self.get_by_id(chunk_id)
        if not chunk:
            return False
        self.db.delete(chunk)
        self.db.commit()
        return True

    def delete_by_document(self, document_id: int) -> int:
        """Remove todos os chunks de um documento e retorna a contagem."""
        count = (
            self.db.query(models.Chunk)
            .filter(models.Chunk.document_id == document_id)
            .delete()
        )
        self.db.commit()
        return count

    def clear_all(self):
        """Remove todos os chunks do banco."""
        self.db.query(models.Chunk).delete()
        self.db.commit()