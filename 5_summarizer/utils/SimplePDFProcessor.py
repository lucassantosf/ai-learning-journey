import PyPDF2
import uuid

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

class SimplePDFProcessor:
    """Handle PDF processing and chunking"""

    def __init__(self,chunk_size=CHUNK_SIZE,chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def read_pdf(self, pdf_file):
        """Read PDF and extract text"""
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text 

    def create_chunks(self, text, pdf_file):
        """Split text into chuncs"""
        chunks = []
        start = 0

        while start < len(text):
            # Find end of chunk
            end = start + self.chunk_size

            # If not at the start, include overlap
            if start > 0:
                start = start - self.chunk_overlap 

            # Get chunk 
            chunk = text[start:end]

            # Try to break at sentence end
            if end < len(text):
                last_period = chunk.rfind(".")
                if last_period != -1:
                    chunk = chunk[: last_period +1]
                    end = start + last_period + 1

            chunks.append(
                {
                    "id": str(uuid.uuid4()),
                    "text":chunk,
                    "metadata":{"source":pdf_file.name},
                }
            )
            start = end 

        return chunks
