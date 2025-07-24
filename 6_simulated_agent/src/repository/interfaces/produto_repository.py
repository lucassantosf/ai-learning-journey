from abc import ABC, abstractmethod
from typing import List
from src.models.produto import Produto

class ProdutoRepository(ABC):
    @abstractmethod
    def listar_todos(self) -> List[Produto]:
        pass

    @abstractmethod
    def buscar_por_id(self, produto_id: str) -> Produto:
        pass

    @abstractmethod
    def criar(self, produto: Produto) -> None:
        pass

    @abstractmethod
    def atualizar(self, produto: Produto) -> None:
        pass

    @abstractmethod
    def deletar(self, produto_id: str) -> None:
        pass
