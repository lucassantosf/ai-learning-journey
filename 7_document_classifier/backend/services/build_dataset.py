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
    if ext == ".pdf":
        parser = PDFParser(str(file_path))
        return parser.extract_text()
    elif ext == ".docx":
        parser = DocxParser(str(file_path))
        return parser.get_text()
    else:
        return ""

def build_dataset():
    vector_store = VectorStore()
    embedder = Embedder()

    for class_dir in DATASET_DIR.iterdir():
        if class_dir.is_dir():
            class_label = class_dir.name
            print(f"Processando classe: {class_label}")

            for file_path in class_dir.glob("*"):
                text = parse_file(file_path)
                if not text.strip():
                    print(f"⚠️ Arquivo vazio ou não suportado: {file_path}")
                    continue

                embedding = embedder.generate_embedding(text)

                vector_store.add(
                    {
                        "doc_id": file_path.stem,
                        "class_label": class_label,
                        "source": str(file_path),
                        "embedding": embedding
                    }
                )

    # Salva em JSON para reuso
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(vector_store.vectors, f, ensure_ascii=False, indent=2)

    print(f"✅ Dataset salvo em {OUTPUT_FILE}")

if __name__ == "__main__":
    build_dataset()