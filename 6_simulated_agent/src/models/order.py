from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class OrderItem:
    product_id: str
    quantity: int
    id: Optional[int] = None  # será preenchido pelo banco

@dataclass
class Order:
    customer_document: str
    customer_name: str
    items: List[OrderItem]
    created_at: datetime = None
    id: Optional[int] = None  # será preenchido pelo banco
    rating: Optional[float] = None

    def __post_init__(self):
        if not self.customer_document or not self.customer_name:
            raise ValueError("User identification is required: customer_document and customer_name must be provided")
