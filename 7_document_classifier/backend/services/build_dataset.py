import os
import json
from pathlib import Path
from backend.services.pdf_parser import PDFParser
from backend.services.docx_parser import DocxParser
from backend.agent.embedder import Embedder
from backend.agent.vector_store import VectorStore

DATASET_DIR = Path(__file__).resolve().parent.parent / "dataset"
OUTPUT_FILE = Path(__file__).resolve().parent.parent / "dataset" / "embeddings.json"


def parse_file(file_path: Path) -> str:
    """Extrai texto de um arquivo PDF ou DOCX."""
    ext = file_path.suffix.lower()
    text = ""

    if ext == ".pdf":
        parser = PDFParser(str(file_path))
        text = parser.extract_text()
    elif ext == ".docx":
        parser = DocxParser(str(file_path))
        text = parser.get_text()

    # Garante que sempre retorna uma string
    if isinstance(text, list):
        text = " ".join(text)

    return text.strip()


def build_dataset():
    vector_store = VectorStore()
    embedder = Embedder()

    for class_dir in DATASET_DIR.iterdir():
        if class_dir.is_dir():
            class_label = class_dir.name
            print(f"Processando classe: {class_label}")

            for file_path in class_dir.glob("*"):
                text = parse_file(file_path)
                if not text:
                    print(f"⚠️ Arquivo vazio ou não suportado: {file_path}")
                    continue

                # Gera embedding do texto (já retorna lista de floats)
                embedding = embedder.generate_embeddings(text)
                print(f"Embedding carregado ({file_path.name}): {len(embedding)} dimensões")

                vector_store.add(
                    embedding,
                    {
                        "doc_id": file_path.stem,
                        "class_label": class_label,
                        "source": str(file_path),
                    }
                )

    # Salva em JSON para reuso
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(vector_store.vectors, f, ensure_ascii=False, indent=2)

    print(f"✅ Dataset salvo em {OUTPUT_FILE}")


def test_search():
    vector_store = VectorStore()
    embedder = Embedder()

    # Carrega dataset salvo
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        for embedding, metadata in dataset:
            vector_store.add(embedding, metadata)

    # Query de teste
    query_text = "THOMAS SMITH"
    query_embedding = embedder.generate_embeddings(query_text)  # lista completa, não apenas o primeiro float

    # Busca
    results = vector_store.search(query_embedding, top_k=3)

    for meta, score in results:
        print(f"{meta['class_label']} - {meta['doc_id']} - Similaridade: {score:.4f}")


if __name__ == "__main__":
    build_dataset()
    # test_search()
