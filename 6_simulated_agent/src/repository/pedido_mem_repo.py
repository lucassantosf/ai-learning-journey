from src.repository.interfaces.pedido_repository import PedidoRepository
from src.models.pedido import Pedido
from typing import Dict, List

class PedidoMemRepository(PedidoRepository):
    def __init__(self):
        self._pedidos: Dict[str, Pedido] = {}

    def listar_todos(self) -> List[Pedido]:
        return list(self._pedidos.values())

    def buscar_por_id(self, pedido_id: str) -> Pedido:
        return self._pedidos.get(pedido_id)

    def criar(self, pedido: Pedido) -> None:
        self._pedidos[pedido.id] = pedido

    def avaliar(self, pedido_id: str, nota: float) -> None:
        if pedido_id in self._pedidos:
            self._pedidos[pedido_id].avaliacao = nota
