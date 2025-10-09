import tempfile
from pathlib import Path
import numpy as np
from storage.json_store import JSONStore
from storage.sqlite_store import SQLiteStore


def create_temp_store(store_type="json"):
    """Cria um repositório temporário, JSON ou SQLite."""
    tmp_dir = Path(tempfile.mkdtemp())
    if store_type == "json":
        store_path = tmp_dir / "test_vectors.json"
        return JSONStore(store_path)
    elif store_type == "sqlite":
        store_path = tmp_dir / "test_vectors.db"
        return SQLiteStore(store_path)
    else:
        raise ValueError(f"Unknown store_type: {store_type}")


def test_persist_and_load():
    """Testa se JSONStore e SQLiteStore conseguem salvar e carregar embeddings."""
    sample_vectors = [
        (np.random.rand(5).tolist(), {"doc_id": "doc1", "class_label": "A"}),
        (np.random.rand(5).tolist(), {"doc_id": "doc2", "class_label": "B"}),
    ]

    for store_type in ["json", "sqlite"]:
        store = create_temp_store(store_type)

        for vec, meta in sample_vectors:
            store.save_vector(vec, meta)

        # Persistir (apenas no JSON, o SQLite já grava direto)
        if hasattr(store, "persist"):
            store.persist()

        loaded = store.load_vectors() if hasattr(store, "load_vectors") else store.load_all()
        assert len(loaded) >= 2, f"{store_type} should return at least 2 vectors"
        assert isinstance(loaded[0][0], list)
        assert isinstance(loaded[0][1], dict)


def test_persistence_between_instances():
    """Testa se dados persistem entre instâncias diferentes."""
    tmp_dir = Path(tempfile.mkdtemp())
    db_path = tmp_dir / "persistent.db"
    store = SQLiteStore(str(db_path))

    vec = np.random.rand(5).tolist()
    meta = {"doc_id": "doc_persist", "class_label": "PersistTest"}
    store.save_vector(vec, meta)

    # Recarrega com nova instância
    store2 = SQLiteStore(str(db_path))
    data = store2.load_all()

    found = any(m["doc_id"] == "doc_persist" for _, m in data)
    assert found, "SQLiteStore should persist data correctly"


def test_similarity_search():
    """Simulação de cálculo de similaridade sem dependência de VectorStore."""
    import numpy as np

    def cosine_similarity(v1, v2):
        a, b = np.array(v1), np.array(v2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    v1 = np.random.rand(10)
    v2 = np.copy(v1)
    v3 = np.random.rand(10)

    sim_same = cosine_similarity(v1, v2)
    sim_diff = cosine_similarity(v1, v3)

    assert sim_same > sim_diff, "Similaridade entre vetores idênticos deve ser maior"