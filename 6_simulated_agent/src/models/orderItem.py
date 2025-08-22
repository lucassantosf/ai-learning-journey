from dataclasses import dataclass

@dataclass
class OrderItem:
    product_id: str
    quantity: int