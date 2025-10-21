import os
from unittest.mock import Mock, patch
import pytest
from src.ingestion.ingestion_pipeline import IngestionPipeline
from reportlab.pdfgen import canvas
from docx import Document


# ==============================
# MOCKS DAS DEPENDÊNCIAS
# ==============================

class MockEmbeddingGenerator:
    def __init__(self, *args, **kwargs):
        pass

    def generate(self, chunks):
        # Simula retorno de embeddings
        # Por exemplo, um vetor com o mesmo tamanho que a quantidade de chunks
        return [[0.1] * 5 for _ in range(len(chunks))]


class MockFaissVectorStore:
    def __init__(self, *args, **kwargs):
        pass

    def add_embeddings(self, *args, **kwargs):
        pass


# ==============================
# FIXTURE GLOBAL (PATCH AUTOMÁTICO)
# ==============================

@pytest.fixture(autouse=True)
def patch_dependencies():
    """
    Aplica mocks automáticos em todas as instâncias do pipeline
    para evitar chamadas reais ao OpenAI e Faiss durante os testes.
    """
    with patch('src.ingestion.ingestion_pipeline.EmbeddingGenerator', MockEmbeddingGenerator):
        with patch('src.ingestion.ingestion_pipeline.FaissVectorStore', MockFaissVectorStore):
            yield


# ==============================
# FUNÇÕES AUXILIARES
# ==============================

def create_test_files():
    """
    Cria arquivos PDF e DOCX simples para uso nos testes.
    """
    base_dir = os.path.join(os.path.dirname(__file__), "../fixtures")
    os.makedirs(base_dir, exist_ok=True)

    # Criar PDF de teste
    pdf_path = os.path.join(base_dir, "test_document.pdf")
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, "Conteúdo de teste para PDF")
    c.save()

    # Criar DOCX de teste
    docx_path = os.path.join(base_dir, "test_document.docx")
    doc = Document()
    doc.add_paragraph("Conteúdo de teste para DOCX")
    doc.save(docx_path)

# ==============================
# TESTES
# ==============================

def test_ingestion_pipeline_initialization():
    """
    Verifica se o pipeline pode ser inicializado sem erros.
    """
    with patch.dict(os.environ, clear=True):
        pipeline = IngestionPipeline()
        assert pipeline is not None


def test_pdf_ingestion():
    """
    Testa o processamento de um arquivo PDF.
    """
    # Preparar o ambiente de teste
    create_test_files()

    # Inicializar o pipeline
    pipeline = IngestionPipeline()

    # Processar arquivo PDF
    pdf_path = os.path.join(os.path.dirname(__file__), "../fixtures/test_document.pdf")
    result = pipeline.process(pdf_path)

    # Verificações
    assert result is not None
    assert 'pages' in result
    assert 'chunks' in result
    assert 'embeddings' in result
    assert result['pages'] > 0
    assert result['chunks'] > 0
    assert result['embeddings'] > 0


def test_docx_ingestion():
    """
    Testa o processamento de um arquivo DOCX.
    """
    # Preparar o ambiente de teste
    create_test_files()

    # Inicializar o pipeline
    pipeline = IngestionPipeline()

    # Processar arquivo DOCX
    docx_path = os.path.join(os.path.dirname(__file__), "../fixtures/test_document.docx")
    result = pipeline.process(docx_path)

    # Verificações
    assert result is not None
    assert 'pages' in result
    assert 'chunks' in result
    assert 'embeddings' in result
    assert result['pages'] > 0
    assert result['chunks'] > 0
    assert result['embeddings'] > 0

def test_unsupported_file_format():
    """
    Testa o comportamento com formato de arquivo não suportado.
    """
    pipeline = IngestionPipeline()

    with pytest.raises(ValueError, match="Formato de arquivo não suportado"):
        pipeline.process('test_document.txt')