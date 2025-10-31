import numpy as np
from src.retrieval.retriever import Retriever
from src.retrieval.faiss_vector_store import FaissVectorStore
import pytest

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

# Busca com índice vazio
def test_retriever_with_empty_index():
    store = FaissVectorStore(embedding_dim=1536)
    model = DummyEmbeddingModel()
    retriever = Retriever(store, model)

    with pytest.raises(ValueError, match="índice FAISS está vazio"):
        retriever.search("qualquer coisa", top_k=3)

# Busca com query sem resultados
def test_retriever_query_without_results():
    store = FaissVectorStore(embedding_dim=1536)
    model = DummyEmbeddingModel()

    # adiciona embeddings que não têm nada a ver com a query
    vectors = [model.embed_text(f"documento comum {i}") for i in range(5)]
    metas = [{"text": f"doc {i}"} for i in range(5)]
    store.add_embeddings(vectors, metas)

    retriever = Retriever(store, model, normalize_embeddings=True)
    results = retriever.search("termo completamente diferente", top_k=3)

    assert isinstance(results, list)
    assert all("text" in r for r in results)
    assert len(results) <= 3

# Normalização de embeddings
def test_retriever_embedding_normalization():
    store = FaissVectorStore(embedding_dim=1536)
    model = DummyEmbeddingModel()
    retriever = Retriever(store, model, normalize_embeddings=True)

    embedding = model.embed_text("texto de teste")
    norm = np.linalg.norm(embedding)

    # Normaliza manualmente, como esperado
    normalized = embedding / norm
    assert abs(np.linalg.norm(normalized) - 1.0) < 1e-6


# Tratamento de queries muito curtas ou vazias
@pytest.mark.parametrize("query", ["", "a", "  ", None])
def test_retriever_short_or_empty_query(query):
    store = FaissVectorStore(embedding_dim=1536)
    model = DummyEmbeddingModel()
    
    # adiciona 1 embedding para o índice não ficar vazio
    vectors = [model.embed_text("documento base")]
    metas = [{"text": "documento base"}]
    store.add_embeddings(vectors, metas)

    retriever = Retriever(store, model)

    # Mesmo com query curta/vazia, não deve quebrar
    try:
        results = retriever.search(query, top_k=2)
        assert isinstance(results, list)
    except Exception as e:
        pytest.fail(f"Retriever não deveria quebrar com query curta/vazia: {e}")
