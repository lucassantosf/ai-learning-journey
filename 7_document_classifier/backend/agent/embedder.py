from typing import List

class Embedder:
    """
    Classe responsável por gerar embeddings de textos.
    Pode usar OpenAI, HuggingFace, etc.
    """

    def __init__(self, model_name: str = "default-embedding-model"):
        self.model_name = model_name
        # Exemplo: inicializar cliente OpenAI ou HuggingFace aqui

    def generate(self, text: str) -> List[float]:
        """
        Gera embedding para um único texto.
        """
        # TODO: implementar chamada ao modelo real
        return [0.0] * 768  # vetor "fake" só para estruturar

    def generate_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos.
        """
        return [self.generate(t) for t in texts]
