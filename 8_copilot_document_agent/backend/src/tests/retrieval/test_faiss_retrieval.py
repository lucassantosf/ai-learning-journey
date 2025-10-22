import os
import numpy as np
import pytest
from src.retrieval.faiss_vector_store import FaissVectorStore


@pytest.fixture
def faiss_store(tmp_path):
    """Inicializa o vetor store FAISS com um arquivo temporário."""
    index_path = tmp_path / "test_faiss_index.bin"
    return FaissVectorStore(path=str(index_path), embedding_dim=6)


@pytest.fixture
def sample_embeddings():
    """Cria embeddings aleatórios de exemplo (10 vetores x 6 dimensões)."""
    np.random.seed(42)
    return np.random.rand(10, 6).astype("float32").tolist()


def test_add_and_count_embeddings(faiss_store, sample_embeddings):
    """Testa se o índice adiciona embeddings corretamente."""
    faiss_store.add_embeddings(sample_embeddings)
    stats = faiss_store.get_stats()

    assert stats["total_vectors"] == len(sample_embeddings)
    assert stats["dimension"] == 6
    print(f"✅ FAISS contém {stats['total_vectors']} vetores após inserção.")


def test_search_returns_results(faiss_store, sample_embeddings):
    """Testa se a busca retorna resultados válidos."""
    faiss_store.add_embeddings(sample_embeddings)
    query = sample_embeddings[0]

    distances, indices = faiss_store.search(query, k=3)

    assert len(indices[0]) == 3
    assert len(distances[0]) == 3
    print(f"✅ Busca retornou índices: {indices[0]} com distâncias: {distances[0]}")


def test_faiss_reconstruct_vectors(faiss_store, sample_embeddings):
    """Reconstrói vetores e valida conteúdo."""
    faiss_store.add_embeddings(sample_embeddings)

    vectors = np.empty((faiss_store.index.ntotal, faiss_store.index.d), dtype="float32")
    faiss_store.index.reconstruct_n(0, faiss_store.index.ntotal, vectors)

    assert vectors.shape == (10, 6)
    print(f"✅ Reconstruídos {vectors.shape[0]} vetores de dimensão {vectors.shape[1]}")


def test_faiss_persistence(tmp_path, sample_embeddings):
    """Testa salvar e recarregar o índice FAISS."""
    index_path = tmp_path / "faiss_persist.bin"
    faiss_store = FaissVectorStore(path=str(index_path), embedding_dim=6)

    faiss_store.add_embeddings(sample_embeddings)
    faiss_store.save()

    reloaded = FaissVectorStore(path=str(index_path), embedding_dim=6)
    stats = reloaded.get_stats()

    assert stats["total_vectors"] == len(sample_embeddings)
    print(f"✅ Índice FAISS recarregado com {stats['total_vectors']} vetores.")
