import math
import pytest
from unittest.mock import patch
from src.ingestion.chunker import Chunker


@patch("src.ingestion.chunker.log_info")
def test_chunker_basic(mock_log):
    text = "palavra " * 1000
    chunker = Chunker(chunk_size=300, overlap=0)
    chunks = chunker.chunk_text([text])

    assert isinstance(chunks, list)
    assert all(isinstance(c, str) for c in chunks)

    expected = math.ceil(1000 / 300)
    assert len(chunks) == expected

    # Agora verificamos se a mensagem inicial foi chamada (não quantas vezes)
    mock_log.assert_any_call("Dividindo texto em chunks com sobreposição de contexto...")

def test_chunker_with_overlap():
    text = "palavra " * 1000  # 1000 palavras
    chunker = Chunker(chunk_size=300, overlap=100)
    chunks = chunker.chunk_text([text])

    # Cada novo chunk começa 200 palavras após o anterior (300 - 100)
    expected = ((1000 - 100) // (300 - 100)) + 1  # fórmula geral para chunks com overlap
    assert len(chunks) == expected

def test_chunker_multiple_texts():
    texts = ["x" * 400, "y" * 200]
    chunker = Chunker(chunk_size=250, overlap=50)
    chunks = chunker.chunk_text(texts)

    # Deve criar chunks para ambos os textos
    assert len(chunks) >= 2
    # Cada chunk deve ser uma string
    assert all(isinstance(c, str) for c in chunks)
    # E deve conter somente 'x' ou 'y' (ou ambos) — sem outros caracteres
    assert set("".join(chunks)).issubset({"x", "y"})


def test_chunker_short_text():
    text = "curto"
    chunker = Chunker(chunk_size=100, overlap=20)
    chunks = chunker.chunk_text([text])

    # Um texto curto deve gerar apenas um chunk
    assert len(chunks) == 1
    assert chunks[0] == "curto"


def test_chunker_empty_text():
    # Conforme implementação atual: texto vazio gera lista vazia
    chunker = Chunker(chunk_size=100, overlap=20)
    chunks = chunker.chunk_text([""])

    assert chunks == []