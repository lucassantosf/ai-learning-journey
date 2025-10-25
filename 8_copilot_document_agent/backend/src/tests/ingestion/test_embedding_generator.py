import pytest
from unittest.mock import patch, MagicMock
from src.ingestion.embedding_generator import EmbeddingGenerator


# ----------------------------
# Teste: inicialização correta
# ----------------------------
@patch("src.ingestion.embedding_generator.OpenAI")
@patch("src.ingestion.embedding_generator.os.getenv")
def test_init_with_valid_api_key(mock_getenv, mock_openai):
    mock_getenv.return_value = "fake-api-key"
    
    generator = EmbeddingGenerator()
    
    mock_getenv.assert_called_once_with("OPENAI_API_KEY")
    assert generator.model == "text-embedding-3-small"
    assert generator.client is not None


# ----------------------------
# Teste: ausência de API key
# ----------------------------
@patch("src.ingestion.embedding_generator.os.getenv")
def test_init_without_api_key(mock_getenv):
    mock_getenv.return_value = None
    
    with pytest.raises(ValueError, match="OpenAI API key not found"):
        EmbeddingGenerator()


# ----------------------------
# Teste: geração de embeddings (fluxo feliz)
# ----------------------------
@patch("src.ingestion.embedding_generator.log_info")
@patch("src.ingestion.embedding_generator.OpenAI")
@patch("src.ingestion.embedding_generator.os.getenv")
def test_generate_embeddings(mock_getenv, mock_openai, mock_log):
    mock_getenv.return_value = "fake-api-key"

    # Mock do client e resposta da API
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
    mock_client.embeddings.create.return_value = mock_response
    mock_openai.return_value = mock_client

    generator = EmbeddingGenerator(model="text-embedding-3-large")
    result = generator.generate(["texto 1", "texto 2"])

    # Verificações
    mock_log.assert_called_once_with("Gerando embeddings com OpenAI...")
    assert isinstance(result, list)
    assert all(isinstance(vec, list) for vec in result)
    assert result == [[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]]
    assert mock_client.embeddings.create.call_count == 2
    mock_client.embeddings.create.assert_any_call(input="texto 1", model="text-embedding-3-large")
    mock_client.embeddings.create.assert_any_call(input="texto 2", model="text-embedding-3-large")


# ----------------------------
# Teste: erro ao criar embedding
# ----------------------------
@patch("src.ingestion.embedding_generator.log_info")
@patch("src.ingestion.embedding_generator.OpenAI")
@patch("src.ingestion.embedding_generator.os.getenv")
def test_generate_raises_from_api(mock_getenv, mock_openai, mock_log):
    mock_getenv.return_value = "fake-api-key"

    mock_client = MagicMock()
    mock_client.embeddings.create.side_effect = Exception("API Error")
    mock_openai.return_value = mock_client

    generator = EmbeddingGenerator()

    with pytest.raises(Exception, match="API Error"):
        generator.generate(["texto falho"])

    mock_log.assert_called_once_with("Gerando embeddings com OpenAI...")