from src.core.models import Chunk
from src.core.logger import log_info
from typing import List

class Chunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, texts: List[str]) -> List[str]:
        log_info("Dividindo texto em chunks...")
        chunks = []
        for text in texts:
            start = 0
            while start < len(text):
                end = start + self.chunk_size
                chunk = text[start:end]
                chunks.append(chunk)
                start += self.chunk_size - self.overlap
        return chunks