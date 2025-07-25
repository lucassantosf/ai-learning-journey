from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class OrderItem:
    product_id: str
    quantity: int

@dataclass
class Order:
    id: str
    items: List[OrderItem]
    creation_date: datetime
    rating: float = None
