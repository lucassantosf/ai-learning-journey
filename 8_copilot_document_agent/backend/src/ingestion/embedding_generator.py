from typing import List
from openai import OpenAI
import os
from dotenv import load_dotenv
from src.core.models import Chunk, EmbeddingVector
from src.core.logger import log_info

load_dotenv()

class EmbeddingGenerator:
    """Gera embeddings usando a API da OpenAI."""

    def __init__(self, model: str = "text-embedding-3-small"):
        # Simplified client initialization
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        # Use minimal initialization to avoid unexpected arguments
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, texts: List[str]) -> List[List[float]]:
        log_info("Gerando embeddings...")
        embeddings = []
        for text in texts:
            response = self.client.embeddings.create(
                input=text,
                model=self.model
            )
            embeddings.append(response.data[0].embedding)
        return embeddings
