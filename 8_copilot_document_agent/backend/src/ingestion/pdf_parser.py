from src.ingestion.parser_base import DocumentParser
from src.core.models import Document
from src.core.logger import log_info

class PDFParser(DocumentParser):
    def parse(self, file_path: str) -> Document:
        log_info(f"Parsing PDF: {file_path}")
        # TODO: Implementar extração real com pdfplumber
        return Document(id="doc1", name=file_path, type="pdf", content="Texto extraído (mock)")
