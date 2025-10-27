import numpy as np
from src.retrieval.retriever import Retriever
from src.retrieval.faiss_vector_store import FaissVectorStore

class DummyEmbeddingModel:
    def embed_text(self, text: str):
        np.random.seed(abs(hash(text)) % (2**32))
        return np.random.rand(1536).astype("float32")

def test_retriever_cosine_search():
    store = FaissVectorStore(embedding_dim=1536)
    model = DummyEmbeddingModel()

    vectors = [model.embed_text(f"documento {i}") for i in range(3)]
    metas = [{"text": f"conteúdo {i}"} for i in range(3)]
    store.add_embeddings(vectors, metas)

    retriever = Retriever(store, model, normalize_embeddings=True)
    results = retriever.search("documento relevante", top_k=2)

    assert isinstance(results, list)
    assert len(results) <= 2
    assert "text" in results[0]
    assert -1 <= results[0]["score"] <= 1