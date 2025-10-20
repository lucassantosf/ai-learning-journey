from abc import ABC, abstractmethod
from typing import List

class DocumentParser(ABC):
    """Interface base para todos os parsers de documentos."""

    @abstractmethod
    def parse(self, file_path: str) -> List[str]:
        """Extrai o texto de um documento e retorna uma lista de páginas ou seções."""
        pass
