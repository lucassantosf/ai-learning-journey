from src.core.models import Chunk, EmbeddingVector
from src.core.logger import log_info

class EmbeddingGenerator:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, chunks: list[Chunk]) -> list[EmbeddingVector]:
        log_info("Gerando embeddings...")
        # TODO: Implementar integração com modelo OpenAI
        return [EmbeddingVector(document_id=c.document_id, text=c.text, embedding=[0.0, 0.0, 0.0]) for c in chunks]