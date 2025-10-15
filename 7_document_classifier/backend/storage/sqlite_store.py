from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from api.core.models import Base, Document, Metadata, Classification, Embedding
 
class SQLiteStore:
    def __init__(self, db_path: str | Path = None):
        base_dir = Path(__file__).resolve().parent.parent
        db_dir = base_dir / "data"
        db_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path or (db_dir / "data.db")
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def save_vector(self, embedding, metadata: dict):
        """
        Salva um embedding e metadados completos no banco, 
        seguindo a estrutura Document / Embedding / Metadata / Classification.
        """
        session = self.SessionLocal()
        try:
            # Try to find an existing document by ID if provided
            doc_id = metadata.get("doc_id")
            existing_doc = None
            
            if doc_id and isinstance(doc_id, (int, str)):
                try:
                    doc_id = int(doc_id)
                    existing_doc = session.query(Document).filter_by(id=doc_id).first()
                except (ValueError, TypeError):
                    pass

            # If no document found by ID, try to find by title
            if not existing_doc:
                existing_doc = session.query(Document).filter_by(title=metadata.get("doc_id", "Unknown")).first()

            # Create a new document only if no existing document is found
            if not existing_doc:
                doc = Document(
                    title=metadata.get("doc_id", "Unknown"),
                    type=metadata.get("class_label", "Unknown"),
                    content=metadata.get("content", ""),
                    created_at=datetime.utcnow()
                )
                session.add(doc)
                session.commit()
                session.refresh(doc)
            else:
                doc = existing_doc

            # Check if embedding already exists for this document
            existing_emb = session.query(Embedding).filter_by(document_id=doc.id).first()
            if not existing_emb:
                emb = Embedding(document_id=doc.id, vector=embedding)
                session.add(emb)

            # Update or create classification
            cls = session.query(Classification).filter_by(document_id=doc.id).first()
            if cls:
                cls.category = metadata.get("class_label")
                cls.confidence = metadata.get("confidence", 1.0)
            else:
                cls = Classification(
                    document_id=doc.id,
                    category=metadata.get("class_label"),
                    confidence=metadata.get("confidence", 1.0)
                )
                session.add(cls)

            # Update or create metadata
            meta = session.query(Metadata).filter_by(document_id=doc.id).first()
            if meta:
                meta.json_data = {
                    "source": metadata.get("source"),
                    "extra": metadata.get("extra", {})
                }
            else:
                meta = Metadata(
                    document_id=doc.id,
                    json_data={
                        "source": metadata.get("source"),
                        "extra": metadata.get("extra", {})
                    }
                )
                session.add(meta)

            session.commit()
            print(f"✅ Documento processado: {doc.title} (ID {doc.id})")

        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao processar documento: {e}")
        finally:
            session.close()

    def load_all(self):
        """
        Carrega todos os embeddings e metadados, 
        retornando no formato [(embedding, metadata_dict)].
        """
        session = self.SessionLocal()
        results = []
        try:
            from api.core.models import Document, Embedding, Classification, Metadata

            query = (
                session.query(Document, Embedding, Classification, Metadata)
                .join(Embedding, Embedding.document_id == Document.id)
                .join(Classification, Classification.document_id == Document.id)
                .join(Metadata, Metadata.document_id == Document.id)
                .all()
            )

            for doc, emb, cls, meta in query:
                embedding = emb.vector
                metadata = {
                    "doc_id": doc.title,
                    "class_label": cls.category,
                    "source": meta.json_data.get("source") if meta and meta.json_data else None,
                    "confidence": cls.confidence,
                }
                results.append((embedding, metadata))

            print(f"📚 Carregados {len(results)} vetores do SQLite.")
            return results

        except Exception as e:
            print(f"❌ Erro ao carregar vetores: {e}")
            return []
        finally:
            session.close()
