import pytest
from unittest.mock import patch
from src.ingestion.docx_parser import DocxParser


@patch("src.ingestion.docx_parser.log_info")
@patch("src.ingestion.docx_parser.docx2txt.process")
def test_parse_valid_file(mock_process, mock_log):
    # Simula um texto retornado pelo docx2txt
    mock_process.return_value = "Este é um documento de teste."

    parser = DocxParser()
    result = parser.parse("../fixtures/test_document.docx")

    # Verifica que o docx2txt foi chamado com o caminho correto
    mock_process.assert_called_once_with("../fixtures/test_document.docx")

    # Verifica que o logger foi chamado
    mock_log.assert_called_once_with("Parsing docx: ../fixtures/test_document.docx")

    # O resultado deve ser uma lista contendo o texto
    assert isinstance(result, list)
    assert result == ["Este é um documento de teste."]


@patch("src.ingestion.docx_parser.log_info")
@patch("src.ingestion.docx_parser.docx2txt.process")
def test_parse_empty_text(mock_process, mock_log):
    # Simula retorno vazio do docx2txt
    mock_process.return_value = ""

    parser = DocxParser()
    result = parser.parse("../fixtures/empty.docx")

    # Deve retornar lista vazia
    assert result == []
    mock_log.assert_called_once_with("Parsing docx: ../fixtures/empty.docx")


@patch("src.ingestion.docx_parser.log_info")
@patch("src.ingestion.docx_parser.docx2txt.process")
def test_parse_none_return(mock_process, mock_log):
    # Simula docx2txt retornando None
    mock_process.return_value = None

    parser = DocxParser()
    result = parser.parse("../fixtures/none.docx")

    # Retorno deve ser lista vazia
    assert result == []
    mock_log.assert_called_once_with("Parsing docx: ../fixtures/none.docx")


@patch("src.ingestion.docx_parser.log_info")
@patch("src.ingestion.docx_parser.docx2txt.process")
def test_parse_raises_exception(mock_process, mock_log):
    # Simula erro do docx2txt
    mock_process.side_effect = FileNotFoundError("Arquivo não encontrado")

    parser = DocxParser()

    with pytest.raises(FileNotFoundError):
        parser.parse("../fixtures/missing.docx")

    mock_log.assert_called_once_with("Parsing docx: ../fixtures/missing.docx")