from src.core.models import Chunk
from src.core.logger import log_info

class Chunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, document_id: str, text: str):
        log_info("Dividindo texto em chunks...")
        # TODO: Implementar chunking real
        return [Chunk(document_id=document_id, text=text, position=0)]