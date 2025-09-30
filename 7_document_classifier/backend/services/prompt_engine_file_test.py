from pathlib import Path
from backend.services.pdf_parser import PDFParser
from backend.services.docx_parser import DocxParser
from backend.agent.prompt_engine import PromptEngine

DATASET_DIR = Path(__file__).resolve().parent.parent / "dataset"

def parse_file(file_path: Path) -> str:
    """Extrai texto do arquivo PDF ou DOCX."""
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return " ".join(PDFParser(str(file_path)).extract_text())
    elif ext == ".docx":
        return DocxParser(str(file_path)).get_text()
    return ""

class PromptEngineFileTester:
    def __init__(self):
        self.engine = PromptEngine()

    def test_category(self, category: str, max_files: int = 2):
        """
        Roda extração nos arquivos reais da pasta dataset/{category}
        """
        folder = DATASET_DIR / category
        if not folder.exists():
            print(f"⚠️ Pasta não encontrada: {folder}")
            return

        for i, file_path in enumerate(folder.glob("*")):
            if i >= max_files:  # limita para não rodar em tudo
                break

            text = parse_file(file_path)
            if not text.strip():
                print(f"⚠️ Arquivo vazio: {file_path}")
                continue

            print(f"\n=== Testando {category} → {file_path.name} ===")
            result = self.engine.extract(category, text)
            print(result)

if __name__ == "__main__":
    """
    This class is executed only for tests and debug purposes only 
    """
    tester = PromptEngineFileTester()
    tester.test_category("resumes")
    tester.test_category("invoices")
    tester.test_category("contracts")
