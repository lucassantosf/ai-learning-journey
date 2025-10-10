import json
from pathlib import Path
from datetime import datetime
from api.core.database import SessionLocal
from api.core.models import Document, Metadata, Classification, Embedding
from storage.sqlite_store import SQLiteStore


class DocumentAgent:
    """
    Camada de persistência desacoplada.
    Pode salvar no banco (SQLite/Postgres) ou em JSON local.
    """

    def __init__(self, mode: str = "sqlite", storage: SQLiteStore = None):
        self.mode = mode
        self.dataset_path = Path(__file__).resolve().parent.parent / "dataset" / "documents.json"
        self.storage = storage  # pode ser injetado pelo pipeline (VectorStore.sqlite)

        if self.mode == "sqlite" and not self.storage:
            # cria um SQLiteStore padrão se nenhum foi passado
            self.storage = SQLiteStore()

        print(f"🧠 DocumentAgent iniciado no modo: {self.mode.upper()}")

    def save(self, data: dict):
        """
        data = {
            "title": str,
            "type": str,
            "content": str,
            "embedding": list[float],
            "classification": str,
            "confidence": float,
            "metadata": dict
        }
        """
        if self.mode == "sqlite":
            return self._save_to_sqlite(data)
        else:
            return self._save_to_json(data)

    # -------------------------------------------------------------------------
    # 📦 Persistência em JSON (modo offline / debug)
    # -------------------------------------------------------------------------
    def _save_to_json(self, data):
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        docs = []
        if self.dataset_path.exists():
            docs = json.loads(self.dataset_path.read_text(encoding="utf-8"))
        data["created_at"] = datetime.utcnow().isoformat()
        docs.append(data)
        self.dataset_path.write_text(json.dumps(docs, indent=2, ensure_ascii=False))
        print(f"💾 Documento salvo em JSON: {data['title']}")
        return {"status": "saved_json", "path": str(self.dataset_path)}

    # -------------------------------------------------------------------------
    # 🧩 Persistência em SQLite (com ORM)
    # -------------------------------------------------------------------------
    def _save_to_sqlite(self, data):
        # caso o agente tenha recebido um SQLiteStore, usamos ele para persistir vetores
        if self.storage:
            print(f"💽 Salvando documento via SQLiteStore ({self.storage.db_path})")

            # Salvamos o vetor diretamente na store
            self.storage.save_vector(data["embedding"], {
                "doc_id": data.get("doc_id", data["title"]),
                "class_label": data["classification"],
                "content": data["content"],
                "source": data["metadata"].get("source", "upload"),
                "confidence": data["confidence"]
            })

        # e também registramos nas tabelas Document, Embedding, etc.
        db = SessionLocal()
        try:
            doc = Document(
                title=data["title"],
                type=data["type"],
                content=data["content"],
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            emb = Embedding(document_id=doc.id, vector=data["embedding"])
            db.add(emb)

            cls = Classification(
                document_id=doc.id,
                category=data["classification"],
                confidence=data["confidence"]
            )
            db.add(cls)

            meta = Metadata(document_id=doc.id, json_data=data["metadata"])
            db.add(meta)

            db.commit()
            print(f"✅ Documento salvo: {data['title']} (ID {doc.id})")

            return {"status": "saved_db", "document_id": doc.id}

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def update_classification(self, document_id: int, correct_class: str, notes: str = None):
        db = SessionLocal()
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if not doc:
                return {"status": "error", "message": "Documento não encontrado"}

            # Atualiza classificação
            cls = db.query(Classification).filter(Classification.document_id == document_id).first()
            if cls:
                cls.category = correct_class
                cls.confidence = 1.0
            else:
                cls = Classification(document_id=doc.id, category=correct_class, confidence=1.0)
                db.add(cls)

            # Nota opcional
            if notes:
                meta = Metadata(document_id=doc.id, json_data={"feedback_notes": notes})
                db.add(meta)

            db.commit()
            return {"status": "success", "document_id": document_id}
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def get_document(self, document_id: int):
        db = SessionLocal()
        try:
            doc = db.query(Document).filter(Document.id == document_id).first()
            if not doc:
                return None
            emb = db.query(Embedding).filter(Embedding.document_id == document_id).first()
            # retorna dict com embedding separado
            return {
                "id": doc.id,
                "title": doc.title,
                "type": doc.type,
                "content": doc.content,
                "embedding": emb.vector if emb else None
            }
        finally:
            db.close()