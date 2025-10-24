from typing import List, Optional
import os
from openai import OpenAI
from src.core.logger import log_info
from dotenv import load_dotenv

load_dotenv()

class EmbeddingGenerator:
    """Gera embeddings usando a API da OpenAI."""

    def __init__(self, model: str = "text-embedding-3-small"):
        # Explicitly check for API key and raise ValueError if not present
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found")
        
        # Explicitly create OpenAI client
        try:
            self._client = OpenAI()
        except Exception as e:
            raise ValueError(f"Failed to initialize OpenAI client: {e}")
        
        self.model = model

    @property
    def client(self) -> Optional[OpenAI]:
        if self._client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                log_info("❌ OPENAI_API_KEY não encontrada. Usando embeddings falsos.")
                return None
            try:
                self._client = OpenAI()
            except Exception as e:
                log_info(f"❌ Erro ao inicializar OpenAI client: {e}")
                return None
        return self._client

    def generate(self, texts: List[str]) -> List[List[float]]:
        if self.client is None:
            log_info("⚠️ OpenAI client não inicializado. Gerando embeddings falsos para teste.")
            # retorna embeddings dummy do mesmo tamanho que texto
            return [[0.0]*1536 for _ in texts]
        
        if not texts:  
            raise ValueError("No texts provided for embedding")

        log_info("Gerando embeddings com OpenAI...")
        
        try:
            embeddings: List[List[float]] = []
            for text in texts:
                response = self._client.embeddings.create(
                    input=text,
                    model=self.model
                )
                embeddings.append(response.data[0].embedding)
            return embeddings
        except Exception as e:
            # Ensure any API errors are properly raised
            raise Exception(f"Failed to generate embeddings: {str(e)}")