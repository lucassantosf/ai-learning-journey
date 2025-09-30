import os
import json
from pathlib import Path
from openai import OpenAI
from backend.agent.embedder import Embedder
from backend.agent.vector_store import VectorStore
from backend.services.pdf_parser import PDFParser
from backend.services.docx_parser import DocxParser
from backend.agent.prompt_engine import PromptEngine

DATASET_FILE = Path(__file__).resolve().parent.parent / "dataset" / "embeddings.json"

def _parse_file(file_path: str) -> str:
    """
    Extrai texto real do arquivo (PDF ou DOCX).
    """
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return " ".join(PDFParser(file_path).extract_text())
    elif ext == ".docx":
        return DocxParser(file_path).get_text()
    return ""

class PromptEngineTester:
    """
    Classe de teste: busca nos embeddings,
    carrega texto real dos documentos,
    e passa para o PromptEngine.
    """

    def __init__(self):
        self.client = OpenAI()
        self.embedder = Embedder()
        self.vector_store = VectorStore()
        self.prompt_engine = PromptEngine()

        # Carrega embeddings existentes
        with open(DATASET_FILE, "r", encoding="utf-8") as f:
            dataset = json.load(f)
            for embedding, metadata in dataset:
                self.vector_store.add(embedding, metadata)

    def query(self, category: str, top_k: int = 1):
        """
        Busca documentos da categoria e roda o extrator específico.
        """
        query_embedding = self.embedder.generate_embeddings(category)
        results = self.vector_store.search(query_embedding, top_k=top_k)

        for meta, score in results:
            file_path = meta.get("source")
            if not file_path or not Path(file_path).exists():
                continue

            text = _parse_file(file_path)
            if not text.strip():
                continue

            # Chama o motor de prompt específico
            return self.prompt_engine.extract(category, text)

        return {"error": "Nenhum documento válido encontrado"}

if __name__ == "__main__":
    """
    This class is executed only for tests and debug purposes only 
    """
    tester = PromptEngineTester()

    # Exemplo 1: currículo
    print("=== TESTE CURRÍCULO ===")
    result = tester.query(category="resumes")
    print(result)

    # Exemplo 2: nota fiscal
    print("\n=== TESTE NOTA FISCAL ===")
    result = tester.query(category="invoices")
    print(result)

    # Exemplo 3: contrato
    print("\n=== TESTE CONTRATO ===")
    result = tester.query(category="contracts")
    print(result)
