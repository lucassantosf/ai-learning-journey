import os
from typing import Dict, Any, List
from src.ingestion.pdf_parser import PDFParser
from src.ingestion.docx_parser import DocxParser
from src.ingestion.text_cleaner import TextCleaner
from src.ingestion.chunker import Chunker
from src.ingestion.embedding_generator import EmbeddingGenerator
from src.retrieval.faiss_vector_store import FaissVectorStore
from src.core.logger import log_info, log_success

class IngestionPipeline:
    """Orquestra todo o fluxo de ingestão de documentos."""

    def __init__(self):
        self.parsers = {
            ".pdf": PDFParser(),
            ".docx": DocxParser()
        }
        self.cleaner = TextCleaner()
        self.chunker = Chunker()
        self.embedding_generator = EmbeddingGenerator()

        # Vector Store path
        vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/faiss_index.bin")
        os.makedirs(os.path.dirname(vector_store_path), exist_ok=True)

        self.vector_store = FaissVectorStore(embedding_dim=1536,path=vector_store_path)

    def process(self, file_path: str) -> Dict[str, Any]:
        log_info(f"🚀 Iniciando pipeline de ingestão para: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.parsers:
            raise ValueError(f"Formato de arquivo não suportado: {ext}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        parser = self.parsers[ext]
        log_info(f"📄 Usando parser: {parser.__class__.__name__}")

        # 1️⃣ Extrair texto
        texts = parser.parse(file_path)
        log_info(f"🧾 Texto extraído de {len(texts)} páginas.")

        # 2️⃣ Limpar texto
        cleaned = self.cleaner.clean(texts)
        log_info("🧹 Texto limpo com sucesso.")

        # 3️⃣ Gerar chunks
        chunks = self.chunker.chunk_text(cleaned)
        log_info(f"✂️ Gerados {len(chunks)} chunks de texto.")

        # 4️⃣ Gerar embeddings
        embeddings_vectors = self.embedding_generator.generate(chunks)
        log_info(f"🧠 Gerados {len(embeddings_vectors)} embeddings.")

        # 5️⃣ Montar listas de vetores e metadados
        vectors = embeddings_vectors
        metadatas = [
            {
                "file_name": os.path.basename(file_path),
                "file_path": os.path.abspath(file_path),
                "chunk_id": i,
                "text": chunks[i],
                "text_preview": chunks[i][:120]
            }
            for i in range(len(chunks))
        ]

        # 6️⃣ Indexar no FAISS
        log_info("💾 Adicionando embeddings ao vetor store FAISS...")
        self.vector_store.add_embeddings(vectors, metadatas)

        if self.vector_store.path:
            self.vector_store.save()

        log_success("✅ Documento processado e indexado com sucesso!")

        return {
            "file": os.path.basename(file_path),
            "pages": len(texts),
            "chunks": len(chunks),
            "embeddings": len(embeddings_vectors)
        }
