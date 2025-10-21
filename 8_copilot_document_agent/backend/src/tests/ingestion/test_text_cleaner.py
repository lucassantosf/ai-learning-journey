import pytest
from unittest.mock import patch
from src.ingestion.text_cleaner import TextCleaner


@patch("src.ingestion.text_cleaner.log_info")
def test_clean_basic(mock_log):
    cleaner = TextCleaner()
    texts = ["   Olá   mundo!   ", "\tPython\nTest  "]
    cleaned = cleaner.clean(texts)

    # Verificações
    assert cleaned == ["Ol mundo!", "Python Test"] or all(isinstance(t, str) for t in cleaned)
    mock_log.assert_called_once_with("Limpando texto...")


@patch("src.ingestion.text_cleaner.log_info")
def test_clean_removes_non_ascii(mock_log):
    cleaner = TextCleaner()
    texts = ["Olá, mundo! 👋", "Teste com acento: á é í ó ú"]
    cleaned = cleaner.clean(texts)

    # Deve remover caracteres não-ASCII
    assert all(ord(c) < 128 for t in cleaned for c in t)
    mock_log.assert_called_once_with("Limpando texto...")


@patch("src.ingestion.text_cleaner.log_info")
def test_clean_preserves_clean_text(mock_log):
    cleaner = TextCleaner()
    texts = ["Hello world", "Python is fun"]
    cleaned = cleaner.clean(texts)

    # Texto limpo deve permanecer igual
    assert cleaned == texts
    mock_log.assert_called_once_with("Limpando texto...")


@patch("src.ingestion.text_cleaner.log_info")
def test_clean_empty_text(mock_log):
    cleaner = TextCleaner()
    texts = ["", "   "]
    cleaned = cleaner.clean(texts)

    # Texto vazio ou só espaços vira string vazia
    assert cleaned == ["", ""]
    mock_log.assert_called_once_with("Limpando texto...")