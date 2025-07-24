from src.repository.interfaces.estoque_repository import EstoqueRepository
from src.models.estoque import Estoque
from typing import Dict, List

class EstoqueMemRepository(EstoqueRepository):
    def __init__(self):
        self._estoque: Dict[str, int] = {}

    def adicionar(self, estoque: Estoque) -> None:
        if estoque.produto_id not in self._estoque:
            self._estoque[estoque.produto_id] = 0
        self._estoque[estoque.produto_id] += estoque.quantidade

    def remover(self, produto_id: str, quantidade: int) -> None:
        if produto_id in self._estoque:
            self._estoque[produto_id] = max(0, self._estoque[produto_id] - quantidade)

    def listar_todos(self) -> List[Estoque]:
        return [Estoque(produto_id=pid, quantidade=qtd) for pid, qtd in self._estoque.items()]
