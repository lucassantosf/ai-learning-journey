# src/db/repositories/document_repository.py

from sqlalchemy.orm import Session
from typing import List, Optional
from src.db import models


class DocumentRepository:
    """
    Repositório responsável por operações no banco para:
    - Documentos
    - Chunks relacionados
    """

    def __init__(self, db: Session):
        self.db = db

    # ======================================================
    # 📄 Documentos
    # ======================================================

    def create_document(self, filename: str, filepath: str, filetype: str) -> models.Document:
        """Cria e persiste um novo documento."""
        doc = models.Document(filename=filename, filepath=filepath, filetype=filetype)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_document(self, document_id: int) -> Optional[models.Document]:
        """Obtém um documento pelo ID."""
        return self.db.query(models.Document).filter(models.Document.id == document_id).first()

    def list_documents(self) -> List[models.Document]:
        """Lista todos os documentos cadastrados."""
        return self.db.query(models.Document).order_by(models.Document.created_at.desc()).all()

    def delete_document(self, document_id: int) -> bool:
        """Remove um documento (e seus chunks/embeddings em cascata)."""
        doc = self.get_document(document_id)
        if not doc:
            return False
        self.db.delete(doc)
        self.db.commit()
        return True

    # ======================================================
    # ✂️ Chunks
    # ======================================================

    def add_chunk(self, document_id: int, content: str, chunk_index: int) -> models.Chunk:
        """Adiciona um chunk de texto vinculado ao documento."""
        chunk = models.Chunk(document_id=document_id, content=content, chunk_index=chunk_index)
        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk

    def get_chunks_by_document(self, document_id: int) -> List[models.Chunk]:
        """Retorna todos os chunks de um documento específico."""
        return (
            self.db.query(models.Chunk)
            .filter(models.Chunk.document_id == document_id)
            .order_by(models.Chunk.chunk_index.asc())
            .all()
        )

    def delete_chunks_by_document(self, document_id: int):
        """Remove todos os chunks vinculados a um documento."""
        self.db.query(models.Chunk).filter(models.Chunk.document_id == document_id).delete()
        self.db.commit()