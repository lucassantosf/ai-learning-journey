import os
import pytest
from backend.services.pdf_parser import PDFParser
from reportlab.pdfgen import canvas

@pytest.fixture
def sample_pdf(tmp_path):
    """
    Cria dinamicamente um PDF de exemplo com texto simples.
    """
    file_path = tmp_path / "sample.pdf"
    c = canvas.Canvas(str(file_path))
    c.drawString(100, 750, "Hello PDF World")
    c.showPage()
    c.save()
    return str(file_path)

class TestPDFParser:
    def test_extract_text_from_pdf(self, sample_pdf):
        parser = PDFParser(sample_pdf)
        textos = parser.extract_text()

        # Verifica que pelo menos 1 página foi lida
        assert len(textos) > 0
        # Verifica que o texto da primeira página contém nossa string
        assert "Hello PDF World" in textos[0]

    def test_empty_pdf(self, tmp_path):
        # cria um PDF vazio
        empty_pdf_path = tmp_path / "empty.pdf"
        c = canvas.Canvas(str(empty_pdf_path))
        c.showPage()
        c.save()

        parser = PDFParser(str(empty_pdf_path))
        textos = parser.extract_text()

        # deve retornar lista com strings vazias
        assert isinstance(textos, list)
        assert textos[0] == ""