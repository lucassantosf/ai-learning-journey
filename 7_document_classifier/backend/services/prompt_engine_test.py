import os
import json
from pathlib import Path
from openai import OpenAI
from backend.agent.embedder import Embedder
from backend.agent.vector_store import VectorStore
from backend.services.pdf_parser import PDFParser
from backend.services.docx_parser import DocxParser


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
    Classe de teste para rodar queries contra embeddings.json,
    mas lendo o conteúdo real dos arquivos (via source).
    """

    def __init__(self):
        self.client = OpenAI()
        self.embedder = Embedder()
        self.vector_store = VectorStore()

        # Carrega embeddings existentes
        with open(DATASET_FILE, "r", encoding="utf-8") as f:
            dataset = json.load(f)
            for embedding, metadata in dataset:
                self.vector_store.add(embedding, metadata)

    def query(self, query_text: str, category: str = None, top_k: int = 3):
        """
        Faz a busca e roda o LLM para extrair informações reais.
        """
        query_embedding = self.embedder.generate_embeddings(query_text)
        results = self.vector_store.search(query_embedding, top_k=top_k)

        # Carrega o texto real de cada documento encontrado
        context_chunks = []
        for meta, score in results:
            file_path = meta.get("source")
            if not file_path or not Path(file_path).exists():
                continue

            text = _parse_file(file_path)
            if not text.strip():
                continue

            context_chunks.append(f"[{meta['class_label']} - {meta['doc_id']}]\n{text[:1500]}")
            # corta para não mandar texto demais (ex: 1500 chars máx por doc)

        if not context_chunks:
            return {"error": "Nenhum documento válido encontrado"}

        context_text = "\n\n".join(context_chunks)

        # Monta o prompt
        prompt = f"""
        Você é um assistente especializado em extração de informações.

        Pergunta do usuário: "{query_text}"
        Categoria esperada: "{category}"

        Contexto extraído dos documentos:
        {context_text}

        Responda de forma objetiva, apenas com a informação solicitada.
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content


if __name__ == "__main__":
    tester = PromptEngineTester()

    # Exemplo 1: currículo
    print("=== TESTE CURRÍCULO ===")
    result = tester.query("Qual é o nome completo do candidato?", category="curriculo")
    print(result)

    # Exemplo 2: nota fiscal
    print("\n=== TESTE NOTA FISCAL ===")
    result = tester.query("Qual é o CNPJ do emitente?", category="nota_fiscal")
    print(result)

    # Exemplo 3: contrato
    print("\n=== TESTE CONTRATO ===")
    result = tester.query("Quais são as partes envolvidas?", category="contrato")
    print(result)
