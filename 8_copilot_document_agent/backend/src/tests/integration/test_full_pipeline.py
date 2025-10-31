import os
import pytest
from unittest.mock import patch, MagicMock

from src.ingestion.ingestion_pipeline import IngestionPipeline

@pytest.fixture
def setup_tmp_dir(tmp_path):
    """Cria diretório temporário e arquivo simulado"""
    pdf_path = tmp_path / "dummy.pdf"
    docx_path = tmp_path / "dummy.docx"
    with open(pdf_path, "w") as f:
        f.write("Texto PDF simulado")
    with open(docx_path, "w") as f:
        f.write("Texto DOCX simulado")
    return str(pdf_path), str(docx_path)


def test_ingestion_pipeline_pdf(setup_tmp_dir):
    pdf_path, _ = setup_tmp_dir
    pipeline = IngestionPipeline()

    with patch.object(pipeline.parsers[".pdf"], "parse", return_value=["Página 1 texto", "Página 2 texto"]) as mock_parse, \
         patch.object(pipeline.cleaner, "clean", return_value=["Texto limpo da página 1", "Texto limpo da página 2"]) as mock_clean, \
         patch.object(pipeline.chunker, "chunk_text", return_value=["chunk1", "chunk2"]) as mock_chunk, \
         patch.object(pipeline.embedding_generator, "generate", return_value=[[0.1]*1536, [0.2]*1536]) as mock_embed, \
         patch.object(pipeline.vector_store, "add_embeddings") as mock_add, \
         patch.object(pipeline.vector_store, "save") as mock_save:
        
        result = pipeline.process(pdf_path)

        assert result["file"] == "dummy.pdf"
        assert result["pages"] == 2
        assert result["chunks"] == 2
        assert result["embeddings"] == 2

        mock_parse.assert_called_once_with(pdf_path)
        mock_clean.assert_called_once()
        mock_chunk.assert_called_once()
        mock_embed.assert_called_once()
        mock_add.assert_called_once()
        mock_save.assert_called_once()


def test_ingestion_pipeline_docx(setup_tmp_dir):
    _, docx_path = setup_tmp_dir
    pipeline = IngestionPipeline()

    with patch.object(pipeline.parsers[".docx"], "parse", return_value=["Texto DOCX completo"]) as mock_parse, \
         patch.object(pipeline.cleaner, "clean", return_value=["Texto DOCX limpo"]) as mock_clean, \
         patch.object(pipeline.chunker, "chunk_text", return_value=["chunk_docx_1", "chunk_docx_2"]) as mock_chunk, \
         patch.object(pipeline.embedding_generator, "generate", return_value=[[0.3]*1536, [0.4]*1536]) as mock_embed, \
         patch.object(pipeline.vector_store, "add_embeddings") as mock_add, \
         patch.object(pipeline.vector_store, "save") as mock_save:
        
        result = pipeline.process(docx_path)

        assert result["file"] == "dummy.docx"
        assert result["pages"] == 1
        assert result["chunks"] == 2
        assert result["embeddings"] == 2

        mock_parse.assert_called_once_with(docx_path)
        mock_clean.assert_called_once()
        mock_chunk.assert_called_once()
        mock_embed.assert_called_once()
        mock_add.assert_called_once()
        mock_save.assert_called_once()


def test_ingestion_pipeline_invalid_format(tmp_path):
    """Verifica que formatos não suportados levantam erro."""
    fake_file = tmp_path / "arquivo.txt"
    fake_file.write_text("Texto qualquer")
    pipeline = IngestionPipeline()
    
    with pytest.raises(ValueError) as e:
        pipeline.process(str(fake_file))
    assert "Formato de arquivo não suportado" in str(e.value)


def test_ingestion_pipeline_missing_file():
    """Verifica erro quando o arquivo não existe."""
    pipeline = IngestionPipeline()
    with pytest.raises(FileNotFoundError):
        pipeline.process("arquivo_inexistente.pdf")


def test_pipeline_vector_store_called_with_correct_metadata(tmp_path):
    """Verifica se metadados estão sendo montados corretamente."""
    pdf_path = tmp_path / "dummy.pdf"
    pdf_path.write_text("Conteúdo fake PDF")

    pipeline = IngestionPipeline()

    mock_chunks = ["chunkA", "chunkB"]
    mock_vectors = [[0.1]*1536, [0.2]*1536]

    with patch.object(pipeline.parsers[".pdf"], "parse", return_value=["texto1", "texto2"]), \
         patch.object(pipeline.cleaner, "clean", return_value=["cleaned1", "cleaned2"]), \
         patch.object(pipeline.chunker, "chunk_text", return_value=mock_chunks), \
         patch.object(pipeline.embedding_generator, "generate", return_value=mock_vectors), \
         patch.object(pipeline.vector_store, "add_embeddings") as mock_add, \
         patch.object(pipeline.vector_store, "save"):

        pipeline.process(str(pdf_path))

        # Checa se os metadados contêm nome e chunk_id corretamente
        args, kwargs = mock_add.call_args
        metadatas = args[1]
        assert all("file_name" in m for m in metadatas)
        assert all("chunk_id" in m for m in metadatas)
        assert len(metadatas) == len(mock_chunks)