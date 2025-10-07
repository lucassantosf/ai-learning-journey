import json
from pathlib import Path
from storage.base_store import BaseStore

class JSONStore(BaseStore):
    def __init__(self, path: Path):
        self.path = path
        self.vectors = []

    def save_vector(self, embedding, metadata):
        self.vectors.append((embedding, metadata))

    def persist(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.vectors, f, ensure_ascii=False, indent=2)

    def load_vectors(self):
        if not self.path.exists():
            return []
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)