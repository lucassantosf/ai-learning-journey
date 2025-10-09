import tempfile
from pathlib import Path
from agent.embedder import Embedder
from agent.vector_store import VectorStore
from storage.sqlite_store import SQLiteStore
from agent.document_agent import DocumentAgent


def test_pipeline_end_to_end(tmp_path: Path):
    """
    Testa o pipeline completo:
    1️⃣ Gera embedding com o Embedder
    2️⃣ Classifica via VectorStore
    3️⃣ Persiste via DocumentAgent (SQLite)
    """

    # 1. Setup temporário
    db_path = tmp_path / "test_pipeline.db"
    storage = SQLiteStore(db_path)
    embedder = Embedder()
    vector_store = VectorStore()
    agent = DocumentAgent(storage=storage)

    # 2. Simula dataset com duas classes
    doc_a = "Contrato de prestação de serviços entre empresa e cliente."
    doc_b = "Recibo de pagamento referente ao mês de setembro."

    emb_a = embedder.generate_embeddings(doc_a)
    emb_b = embedder.generate_embeddings(doc_b)

    vector_store.add(emb_a, {"class_label": "contrato", "doc_id": "a"})
    vector_store.add(emb_b, {"class_label": "recibo", "doc_id": "b"})

    # 3. Persiste esses embeddings no banco (para simular build_dataset real)
    storage.save_vector(emb_a, {
        "doc_id": "a",
        "class_label": "contrato",
        "content": doc_a,
        "source": "simulado",
        "confidence": 1.0
    })
    storage.save_vector(emb_b, {
        "doc_id": "b",
        "class_label": "recibo",
        "content": doc_b,
        "source": "simulado",
        "confidence": 1.0
    })

    # 4. Executa uma nova classificação
    new_text = "Contrato firmado com fornecedor para prestação de serviços."
    query_embedding = embedder.generate_embeddings(new_text)
    predicted_class, confidence, _ = vector_store.predict_class(query_embedding)

    assert predicted_class in ["contrato", "recibo"]
    assert 0 <= confidence <= 1

    # 5. Persiste o documento classificado no banco
    result = agent.save({
        "title": "teste_contrato.pdf",
        "type": predicted_class,
        "content": new_text,
        "embedding": query_embedding,
        "classification": predicted_class,
        "confidence": float(confidence),
        "metadata": {"source": "teste"}
    })

    # 6. Verifica persistência no banco
    all_vectors = storage.load_all()
    assert len(all_vectors) >= 3  # 2 iniciais + 1 salvo pelo agente
    print("\n✅ Teste de integração pipeline passou com sucesso!")