import json
from pathlib import Path
from datetime import datetime
from api.core.database import SessionLocal
from api.core.models import Document, Metadata, Classification, Embedding

class DocumentAgent:
    """
    Camada de persistência desacoplada.
    Decide se salva em banco ou JSON, conforme config.
    """

    MODE = "sqlite"  # ou "json"

    def __init__(self):
        self.dataset_path = Path(__file__).resolve().parent.parent / "dataset" / "documents.json"

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
        if self.MODE == "sqlite":
            return self._save_to_db(data)
        else:
            return self._save_to_json(data)

    def _save_to_json(self, data):
        self.dataset_path.parent.mkdir(parents=True, exist_ok=True)
        docs = []
        if self.dataset_path.exists():
            docs = json.loads(self.dataset_path.read_text(encoding="utf-8"))
        data["created_at"] = datetime.utcnow().isoformat()
        docs.append(data)
        self.dataset_path.write_text(json.dumps(docs, indent=2, ensure_ascii=False))
        return {"status": "saved_json", "path": str(self.dataset_path)}

    def _save_to_db(self, data):
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
            return {"status": "saved_db", "document_id": doc.id}
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()