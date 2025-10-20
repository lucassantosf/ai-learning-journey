import pdfplumber
from typing import List
from src.ingestion.parser_base import DocumentParser
from src.core.models import Document
from src.core.logger import log_info

class PDFParser(DocumentParser):
    def parse(self, file_path: str) -> List[str]:
        log_info(f"Parsing PDF: {file_path}")
        texts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                texts.append(text)
        return texts
