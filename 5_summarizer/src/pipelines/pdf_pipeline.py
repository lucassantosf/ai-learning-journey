from src.core.chunking import TextChunker
from PyPDF2 import PdfReader
import re

def clean_text(text):
    """Clean raw PDF text."""
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove extra spaces before punctuation
    text = re.sub(r'\s+([.,!?;])', r'\1', text)
    return text.strip()

def process_pdf_file(pdf_stream):
    """Read PDF and return clean chunks with metadata"""
    chunker = TextChunker()

    reader = PdfReader(pdf_stream)
    all_text = ""
    page_chunks = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        page_text = clean_text(page_text)

        if page_text:
            all_text += page_text + "\n\n"
            page_chunks.append({"page": page_number, "text": page_text})

    # Create semantic chunks of the entire document (avoid page-by-page cutting)
    chunks = chunker.create_chunks(all_text, source=getattr(pdf_stream, "name", "uploaded_file.pdf"))

    return chunks
