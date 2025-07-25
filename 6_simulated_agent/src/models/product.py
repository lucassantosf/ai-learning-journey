from dataclasses import dataclass

@dataclass
class Product:
    id: str
    name: str
    price: float
    quantity: int
    average_rating: float
