from src.core.chunking import TextChunker
from PyPDF2 import PdfReader
import re

def clean_text(text):
    """Limpa texto bruto do PDF."""
    # Remove múltiplos espaços
    text = re.sub(r'\s+', ' ', text)
    # Remove espaços extras antes de pontuação
    text = re.sub(r'\s+([.,!?;])', r'\1', text)
    return text.strip()

def process_pdf_file(pdf_stream):
    """Lê PDF e retorna chunks limpos com metadados"""
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

    # Cria chunks semânticos do documento inteiro (evita corte página a página)
    chunks = chunker.create_chunks(all_text, source=getattr(pdf_stream, "name", "uploaded_file.pdf"))

    return chunks 