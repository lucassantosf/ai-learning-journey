from dataclasses import dataclass

@dataclass
class Inventory:
    product_id: str
    quantity: int
    product_name: str = None   