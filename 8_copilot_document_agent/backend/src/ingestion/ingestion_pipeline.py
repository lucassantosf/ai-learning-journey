import os
from typing import Optional
from src.ingestion.pdf_parser import PDFParser
from src.ingestion.docx_parser import DocxParser
from src.ingestion.text_cleaner import TextCleaner
from src.ingestion.chunker import Chunker
from src.ingestion.embedding_generator import EmbeddingGenerator
from src.retrieval.faiss_vector_store import FaissVectorStore
from src.core.config import Config
from src.core.logger import log_info, log_success

class IngestionPipeline:
    def __init__(self):
        self.parsers = {
            ".pdf": PDFParser(),
            ".docx": DocxParser()
        }
        self.cleaner = TextCleaner()
        self.chunker = Chunker()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = FaissVectorStore()

    def process(self, file_path: str):
        log_info(f"Iniciando pipeline para {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext not in self.parsers:
            raise ValueError(f"Formato de arquivo não suportado: {ext}")

        parser = self.parsers[ext]

        texts = parser.parse(file_path)
        cleaned = self.cleaner.clean(texts)
        chunks = self.chunker.chunk_text(cleaned)
        embeddings = self.embedding_generator.generate(chunks)
        self.vector_store.add_embeddings(embeddings)

        log_success("Documento processado e indexado com sucesso!")

        return {
            "pages": len(texts),
            "chunks": len(chunks),
            "embeddings": len(embeddings)
        }