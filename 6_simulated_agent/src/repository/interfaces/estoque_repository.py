from abc import ABC, abstractmethod
from typing import List
from src.models.estoque import Estoque

class EstoqueRepository(ABC):
    @abstractmethod
    def adicionar(self, estoque: Estoque) -> None:
        pass

    @abstractmethod
    def remover(self, produto_id: str, quantidade: int) -> None:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Estoque]:
        pass
