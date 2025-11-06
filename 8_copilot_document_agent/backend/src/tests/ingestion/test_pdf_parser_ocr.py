from src.ingestion.pdf_parser import PDFParser
import os

def test_pdf_parser_with_ocr():
    parser = PDFParser()

    # Caminho absoluto para o PDF de fixture
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "fixtures", "test_document.pdf")
    pdf_path = os.path.abspath(pdf_path)

    texts = parser.parse(pdf_path)
    assert isinstance(texts, list)
    assert len(texts) > 0