from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class OrderItem:
    product_id: str
    quantity: int

@dataclass
class Order:
    id: str
    user_id: str
    customer_name: str
    items: List[OrderItem]
    creation_date: datetime
    rating: float = None

    def __post_init__(self):
        """
        Validate that user identification is provided
        """
        if not self.user_id or not self.customer_name:
            raise ValueError("User identification is required: user_id and customer_name must be provided")
