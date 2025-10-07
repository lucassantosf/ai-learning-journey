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
            doc = Document(
                title=metadata.get("doc_id", "Unknown"),
                type=metadata.get("class_label", "Unknown"),
                content=metadata.get("content", ""),
                created_at=datetime.utcnow()
            )
            session.add(doc)
            session.commit()
            session.refresh(doc)

            emb = Embedding(document_id=doc.id, vector=embedding)
            session.add(emb)

            cls = Classification(
                document_id=doc.id,
                category=metadata.get("class_label"),
                confidence=metadata.get("confidence", 1.0)
            )
            session.add(cls)

            meta = Metadata(
                document_id=doc.id,
                json_data={
                    "source": metadata.get("source"),
                    "extra": metadata.get("extra", {})
                }
            )
            session.add(meta)

            session.commit()
            print(f"✅ Documento salvo: {doc.title} (ID {doc.id})")

        except Exception as e:
            session.rollback()
            print(f"❌ Erro ao salvar documento: {e}")
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
            docs = session.query(Document).all()
            for doc in docs:
                embedding = (
                    doc.embedding.vector if doc.embedding else []
                )
                meta = {
                    "doc_id": doc.title,
                    "class_label": doc.type,
                    "source": doc.document_metadata.json_data.get("source") if doc.document_metadata else None,
                }
                results.append((embedding, meta))
        finally:
            session.close()

        return results