import pytest
from unittest.mock import patch, MagicMock
from src.ingestion.pdf_parser import PDFParser
from unittest.mock import MagicMock

@patch("src.ingestion.pdf_parser.log_info")
@patch("src.ingestion.pdf_parser.pdfplumber.open")
def test_parse_pdf_multiple_pages(mock_open, mock_log):
    # Mock das páginas do PDF
    page1 = MagicMock()
    page1.extract_text.return_value = "Texto da página 1"
    page2 = MagicMock()
    page2.extract_text.return_value = "Texto da página 2"
    mock_pdf = MagicMock()
    mock_pdf.pages = [page1, page2]
    mock_open.return_value.__enter__.return_value = mock_pdf

    parser = PDFParser()
    result = parser.parse("../fixtures/test_document.pdf")

    # Verificações
    mock_open.assert_called_once_with("../fixtures/test_document.pdf")
    mock_log.assert_called_once_with("Parsing PDF: ../fixtures/test_document.pdf")
    assert isinstance(result, list)
    assert result == ["Texto da página 1", "Texto da página 2"]


@patch("src.ingestion.pdf_parser.log_info")
@patch("src.ingestion.pdf_parser.pdfplumber.open")
def test_parse_pdf_page_none(mock_open, mock_log):
    # Mock de página que retorna None
    page = MagicMock()
    page.extract_text.return_value = None
    mock_pdf = MagicMock()
    mock_pdf.pages = [page]
    mock_open.return_value.__enter__.return_value = mock_pdf

    parser = PDFParser()
    result = parser.parse("../fixtures/page_none.pdf")

    # Deve substituir None por string vazia
    assert result == [""]


@patch("src.ingestion.pdf_parser.log_info")
@patch("src.ingestion.pdf_parser.pdfplumber.open")
def test_parse_pdf_raises_exception(mock_open, mock_log):
    # Força exceção do pdfplumber
    mock_open.side_effect = FileNotFoundError("Arquivo não encontrado")

    parser = PDFParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("../fixtures/missing.pdf")

    mock_log.assert_called_once_with("Parsing PDF: ../fixtures/missing.pdf")

# Arquivo inexistente
def test_pdf_parser_file_not_found():
    parser = PDFParser()
    with pytest.raises(FileNotFoundError):
        parser.parse("arquivo_inexistente.pdf")

@patch("pdfplumber.open")
def test_pdf_parser_empty_pages(mock_open):  # <-- nome correto do mock
    mock_page = MagicMock()
    mock_page.extract_text.return_value = None

    mock_pdf = MagicMock()
    mock_pdf.__enter__.return_value = mock_pdf
    mock_pdf.pages = [mock_page]

    mock_open.return_value = mock_pdf

    parser = PDFParser()
    texts = parser.parse("fake.pdf")
    assert texts == [""]