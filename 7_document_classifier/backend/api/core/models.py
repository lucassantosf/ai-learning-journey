from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from api.core.database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)  # resume, invoice, contract
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    document_metadata = relationship("Metadata", back_populates="document", uselist=False)
    embedding = relationship("Embedding", back_populates="document", uselist=False)
    classification = relationship("Classification", back_populates="document", uselist=False)


class Metadata(Base):
    __tablename__ = "metadata"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    json_data = Column(JSON)

    document = relationship("Document", back_populates="document_metadata")  # ✅ atualizado


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    vector = Column(JSON)

    document = relationship("Document", back_populates="embedding")


class Classification(Base):
    __tablename__ = "classifications"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    category = Column(String)
    confidence = Column(Float)

    document = relationship("Document", back_populates="classification")