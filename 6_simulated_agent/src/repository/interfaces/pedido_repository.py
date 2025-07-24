from abc import ABC, abstractmethod
from typing import List
from src.models.pedido import Pedido

class PedidoRepository(ABC):
    @abstractmethod
    def listar_todos(self) -> List[Pedido]:
        pass

    @abstractmethod
    def buscar_por_id(self, pedido_id: str) -> Pedido:
        pass

    @abstractmethod
    def criar(self, pedido: Pedido) -> None:
        pass

    @abstractmethod
    def avaliar(self, pedido_id: str, nota: float) -> None:
        pass
