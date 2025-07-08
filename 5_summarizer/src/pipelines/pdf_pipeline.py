from src.core.chunking import TextChunker
import PyPDF2

def process_pdf_file(file_path):
    chunker = TextChunker()
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        text = "\n".join(page.extract_text() for page in reader.pages)
    return chunker.create_chunks(text, source=file_path)
