from abc import ABC, abstractmethod
from src.core.models import Document

class DocumentParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> Document:
        """Extrai texto e metadados de um arquivo e retorna um Document"""
        pass
