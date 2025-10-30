from src.core.models import Chunk
from src.core.logger import log_info
from typing import List

class Chunker:
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        """
        chunk_size: número de tokens (aqui aproximamos por palavras)
        overlap: número de palavras de sobreposição entre chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, texts: List[str]) -> List[str]:
        log_info("Dividindo texto em chunks com sobreposição de contexto...")
        chunks = []

        for text in texts:
            # Divide o texto em palavras
            words = text.split()
            start = 0

            while start < len(words):
                end = start + self.chunk_size
                chunk_words = words[start:end]
                chunk = " ".join(chunk_words)
                chunks.append(chunk)

                # Avança o início, mantendo a sobreposição
                start += self.chunk_size - self.overlap

                # Evita loop infinito se overlap >= chunk_size
                if self.overlap >= self.chunk_size:
                    break

        log_info(f"✂️ Gerados {len(chunks)} chunks de texto (com sobreposição).")
        return chunks