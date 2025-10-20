import os
from unittest.mock import Mock, patch
import pytest
from src.ingestion.ingestion_pipeline import IngestionPipeline
from reportlab.pdfgen import canvas
from docx import Document

# Substitua as classes para testes
class MockEmbeddingGenerator:
    def __init__(self, *args, **kwargs):
        pass

class MockFaissVectorStore:
    def __init__(self, *args, **kwargs):
        pass
    def add_embeddings(self, *args, **kwargs):
        pass

def test_ingestion_pipeline_initialization():
    # Substituir completamente as classes por mocks
    with patch('src.ingestion.ingestion_pipeline.EmbeddingGenerator', 
               MockEmbeddingGenerator):
        with patch('src.ingestion.ingestion_pipeline.FaissVectorStore', 
                   MockFaissVectorStore):
            # Remover qualquer variável de ambiente que possa interferir
            with patch.dict(os.environ, clear=True):
                pipeline = IngestionPipeline()
                assert pipeline is not None

# Crie uma pasta de fixtures com arquivos de teste
def create_test_files():
    # Crie um diretório para fixtures se não existir
    os.makedirs('tests/fixtures', exist_ok=True)
    
    # Criar PDF de teste
    pdf_path = 'tests/fixtures/test_document.pdf'
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, "Conteúdo de teste para PDF")
    c.save()
    
    # Criar DOCX de teste
    docx_path = 'tests/fixtures/test_document.docx'
    doc = Document()
    doc.add_paragraph("Conteúdo de teste para DOCX")
    doc.save(docx_path)

def test_pdf_ingestion():
    # Preparar o ambiente de teste
    create_test_files()
    
    # Inicializar o pipeline
    pipeline = IngestionPipeline()
    
    # Processar arquivo PDF
    pdf_path = 'fixtures/test_document.pdf'
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
    # Preparar o ambiente de teste
    create_test_files()
    
    # Inicializar o pipeline
    pipeline = IngestionPipeline()
    
    # Processar arquivo DOCX
    docx_path = 'fixtures/test_document.docx'
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
    # Testar comportamento com formato não suportado
    pipeline = IngestionPipeline()
    
    with pytest.raises(ValueError, match="Formato de arquivo não suportado"):
        pipeline.process('test_document.txt')