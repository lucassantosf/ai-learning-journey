from src.ingestion.pdf_parser import PDFParser
from src.ingestion.text_cleaner import TextCleaner
from src.ingestion.chunker import Chunker
from src.ingestion.embedding_generator import EmbeddingGenerator
from src.retrieval.faiss_vector_store import FaissVectorStore
from src.core.config import Config
from src.core.logger import log_info, log_success


class IngestionPipeline:
    def __init__(self):
        self.parser = PDFParser()
        self.cleaner = TextCleaner()
        self.chunker = Chunker()
        self.embedder = EmbeddingGenerator(Config.EMBEDDING_MODEL)
        self.vector_store = FaissVectorStore(Config.VECTOR_STORE_PATH)

    def process(self, file_path: str):
        log_info(f"Iniciando pipeline para {file_path}")

        document = self.parser.parse(file_path)
        cleaned_text = self.cleaner.clean(document.content)
        chunks = self.chunker.chunk_text(document.id, cleaned_text)
        embeddings = self.embedder.generate(chunks)
        self.vector_store.add_embeddings(embeddings)

        log_success("Documento processado e indexado com sucesso!")
        return {"document_id": document.id, "status": "success"}