from src.core.chunking import TextChunker
from PyPDF2 import PdfReader

def process_pdf_file(pdf_stream):
    """Recebe stream de PDF e retorna os chunks"""
    chunker = TextChunker()
    reader = PdfReader(pdf_stream)
    text = "\n".join([page.extract_text() for page in reader.pages])
    return chunker.create_chunks(text, source=getattr(pdf_stream, "name", "uploaded_file.pdf"))