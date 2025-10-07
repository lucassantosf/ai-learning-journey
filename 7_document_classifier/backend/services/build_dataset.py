import os
import json
from pathlib import Path
from services.pdf_parser import PDFParser
from services.docx_parser import DocxParser
from agent.embedder import Embedder
from agent.vector_store import VectorStore
from storage.sqlite_store import SQLiteStore

# Caminhos principais
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "dataset"
OUTPUT_FILE = DATASET_DIR / "embeddings.json"

# Modo de armazenamento: "sqlite" ou "json"
STORAGE_MODE = "sqlite"

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

    if isinstance(text, list):
        text = " ".join(text)

    return text.strip()


def build_dataset():
    print(f"\n📦 Iniciando build_dataset() — modo: {STORAGE_MODE.upper()}")

    embedder = Embedder()
    vector_store = VectorStore()
    storage = None

    if STORAGE_MODE == "sqlite":
        print("💾 Usando SQLiteStore para persistência...")
        storage = SQLiteStore()
    else:
        print("📄 Usando JSON local como fallback.")

    # Garantir que pasta de dataset existe
    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    for class_dir in DATASET_DIR.iterdir():
        if not class_dir.is_dir():
            continue

        class_label = class_dir.name
        print(f"\n🔹 Processando classe: {class_label}")

        for file_path in class_dir.glob("*"):
            if not file_path.is_file():
                continue

            text = parse_file(file_path)
            if not text:
                print(f"⚠️ Arquivo vazio ou não suportado: {file_path}")
                continue

            # Gera embedding
            embedding = embedder.generate_embeddings(text)
            print(f"✅ Embedding ({file_path.name}): {len(embedding)} dimensões")

            metadata = {
                "doc_id": file_path.stem,
                "class_label": class_label,
                "source": str(file_path),
                "content": text,
                "confidence": 1.0
            }

            # Adiciona no vector store local (para buscas e JSON)
            vector_store.add(embedding, metadata)

            # Persiste conforme modo
            if STORAGE_MODE == "sqlite":
                storage.save_vector(embedding, metadata)

    if STORAGE_MODE == "json":
        print("\n💾 Salvando dataset em JSON...")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(vector_store.vectors, f, ensure_ascii=False, indent=2)
        print(f"✅ Dataset salvo em {OUTPUT_FILE}")

    print("\n🎯 Build finalizado com sucesso!")


def test_search():
    """Testa buscas de similaridade usando o JSON ou o banco."""
    embedder = Embedder()
    vector_store = VectorStore()

    if STORAGE_MODE == "sqlite":
        storage = SQLiteStore()
        dataset = storage.load_all()
    else:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            dataset = json.load(f)

    for embedding, metadata in dataset:
        vector_store.add(embedding, metadata)

    query_text = "THOMAS SMITH"
    query_embedding = embedder.generate_embeddings(query_text)
    results = vector_store.search(query_embedding, top_k=3)

    print("\n🔍 Resultados da busca:")
    for meta, score in results:
        print(f" - {meta['class_label']} | {meta['doc_id']} | Similaridade: {score:.4f}")

if __name__ == "__main__":
    # build_dataset()
    test_search()