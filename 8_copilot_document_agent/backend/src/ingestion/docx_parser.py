import docx2txt
from typing import List
from src.ingestion.parser_base import DocumentParser
from src.core.models import Document
from src.core.logger import log_info

class DocxParser(DocumentParser):
    def parse(self, file_path: str) -> List[str]:
        log_info(f"Parsing docx: {file_path}")
        text = docx2txt.process(file_path)
        return [text] if text else []