from dataclasses import dataclass

@dataclass
class Produto:
    id: str
    nome: str
    quantidade: int
    avaliacao_media: float
    preco: float