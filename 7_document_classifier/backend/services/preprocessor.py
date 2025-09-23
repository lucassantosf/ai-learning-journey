from typing import List

class Preprocessor:
    """
    Faz limpeza e chunking de textos antes de gerar embeddings.
    """

    def clean_text(self, text: str) -> str:
        # TODO: remover caracteres estranhos, normalizar
        return text.strip()

    def chunk_text(self, text: str, max_length: int = 500) -> List[str]:
        """
        Divide o texto em pedaços menores para embedding.
        """
        words = text.split()
        chunks, current = [], []

        for word in words:
            if len(" ".join(current + [word])) > max_length:
                chunks.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            chunks.append(" ".join(current))
        return chunks
