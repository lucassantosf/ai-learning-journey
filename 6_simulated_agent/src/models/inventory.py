from dataclasses import dataclass
from typing import Optional

@dataclass
class Inventory:
    product_id: str
    quantity: int
    product_name: Optional[str] = None