import numpy as np
from dotenv import load_dotenv
from typing import List
from openai import OpenAI
import tiktoken

load_dotenv()

class Embedder:
    """
    Classe responsável por gerar embeddings de textos.
    Pode usar OpenAI, HuggingFace, etc.
    """

    def __init__(self, model_name: str = "text-embedding-3-small"):
        self.model_name = model_name
        self.client = OpenAI()
        self.tokenizer = tiktoken.get_encoding("cl100k_base")  # tokenizer compatível

    def _chunk_text(self, text: str, max_tokens: int = 8000) -> List[str]:
        """
        Divide o texto em chunks menores para caber no modelo.
        """
        tokens = self.tokenizer.encode(text)
        chunks = []
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i+max_tokens]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
        return chunks

    def generate_embeddings(self, text: str) -> List[float]:
        """
        Gera embedding para um único texto (pode dividir em chunks se for muito longo).
        Retorna a média dos embeddings dos chunks.
        """
        chunks = self._chunk_text(text)

        embeddings = []
        for chunk in chunks:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=chunk
            )
            embeddings.append(response.data[0].embedding)

        # 🔹 Se o texto for muito longo, tira a média dos embeddings
        if len(embeddings) > 1:
            return np.mean(embeddings, axis=0).tolist()
        return embeddings[0]

    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos.
        """
        response = self.client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        return [item.embedding for item in response.data]
