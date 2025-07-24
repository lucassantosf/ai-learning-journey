from src.repository.interfaces.produto_repository import ProdutoRepository
from src.models.produto import Produto
from typing import Dict, List
from src.utils.helpers import get_produtos

class ProdutoMemRepository(ProdutoRepository):
    def __init__(self):
        self._produtos: Dict[str, Produto] = get_produtos()

    def listar_todos(self) -> List[Produto]:
        return list(self._produtos.values())

    def buscar_por_id(self, produto_id: str) -> Produto:
        return self._produtos.get(produto_id)

    def criar(self, produto: Produto) -> None:
        self._produtos[produto.id] = produto

    def atualizar(self, produto: Produto) -> None:
        if produto.id in self._produtos:
            self._produtos[produto.id] = produto

    def deletar(self, produto_id: str) -> None:
        if produto_id in self._produtos:
            del self._produtos[produto_id]
