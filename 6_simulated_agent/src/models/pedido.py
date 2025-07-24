from dataclasses import dataclass, field
from typing import List
from datetime import datetime

@dataclass
class ItemPedido:
    produto_id: str
    quantidade: int

@dataclass
class Pedido:
    id: str
    itens: List[ItemPedido]
    data_criacao: datetime
    avaliacao: float = field(default=None)  # Avaliação opcional
