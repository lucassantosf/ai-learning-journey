import pytest
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

@pytest.mark.parametrize("category", ["contracts", "invoices", "resumes"])
def test_prompt_engine_with_real_files(category):
    """
    Testa o PromptEngine com exemplos reais da pasta dataset/{category}.
    """
    folder = DATASET_DIR / category
    assert folder.exists(), f"Pasta {category} não encontrada em {folder}"

    files = list(folder.glob("*"))
    assert files, f"Nenhum arquivo de teste encontrado em {folder}"

    engine = PromptEngine()

    for file_path in files[:1]:  # limita para não rodar em tudo
        text = parse_file(file_path)
        assert text.strip(), f"Arquivo vazio: {file_path}"

        result = engine.extract(category, text)

        # Verificações básicas — ajusta conforme necessidade
        assert isinstance(result, dict), f"Resultado não é JSON para {file_path}"
        assert "error" not in result, f"Erro retornado: {result.get('error')}"
        assert len(result.keys()) > 0, f"Nenhum campo extraído de {file_path}"
