import math
import pytest
from unittest.mock import patch
from src.ingestion.chunker import Chunker


@patch("src.ingestion.chunker.log_info")
def test_chunker_basic(mock_log):
    text = "a" * 1000
    chunker = Chunker(chunk_size=300, overlap=0)
    chunks = chunker.chunk_text([text])

    # Verificações básicas
    assert isinstance(chunks, list)
    assert all(isinstance(c, str) for c in chunks)

    # Esperamos ceil(len(text) / chunk_size) chunks quando overlap == 0
    expected = math.ceil(len(text) / 300)
    assert len(chunks) == expected

    # Verifica se o logger foi chamado corretamente
    mock_log.assert_called_once_with("Dividindo texto em chunks...")


def test_chunker_with_overlap():
    text = "a" * 1000
    chunker = Chunker(chunk_size=300, overlap=100)
    chunks = chunker.chunk_text([text])

    # Deve ter mais chunks do que sem overlap (4 sem overlap)
    assert len(chunks) > 4
    # E os tamanhos individuais devem respeitar o limite máximo
    assert all(len(c) <= 300 for c in chunks)


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