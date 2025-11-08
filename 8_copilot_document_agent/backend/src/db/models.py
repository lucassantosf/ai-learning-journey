# src/db/models.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from src.db.database import Base


# ======================================================
# 📄 Documento
# ======================================================

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False)
    filetype = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}')>"


# ======================================================
# ✂️ Chunk de Texto
# ======================================================

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"))
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    document = relationship("Document", back_populates="chunks")
    embedding = relationship("Embedding", back_populates="chunk", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Chunk(id={self.id}, doc_id={self.document_id}, index={self.chunk_index})>"


# ======================================================
# 🧠 Embedding (vetor FAISS + metadados)
# ======================================================

class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, ForeignKey("chunks.id", ondelete="CASCADE"))
    vector = Column(JSON, nullable=False)  # Armazena o vetor como lista (float[])
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento
    chunk = relationship("Chunk", back_populates="embedding")

    def __repr__(self):
        return f"<Embedding(id={self.id}, chunk_id={self.chunk_id})>"


# ======================================================
# 💬 Consultas do usuário
# ======================================================

class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    responses = relationship("Response", back_populates="query", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Query(id={self.id}, question='{self.question[:30]}...')>"


# ======================================================
# 💬 Respostas do modelo
# ======================================================

class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id", ondelete="CASCADE"))
    answer = Column(Text, nullable=False)
    data = Column(JSON, name="metadata")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamento
    query = relationship("Query", back_populates="responses")

    def __repr__(self):
        return f"<Response(id={self.id}, query_id={self.query_id})>"