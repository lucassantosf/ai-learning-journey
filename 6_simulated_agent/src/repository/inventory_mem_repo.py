from typing import Dict, List
from src.repository.interfaces.inventory_repository import InventoryRepository
from src.models.inventory import Inventory

class InventoryMemRepository(InventoryRepository):
    def __init__(self):
        from src.utils.helpers import get_products
        self._inventory: Dict[str, int] = {
            product_id: product.quantity 
            for product_id, product in get_products().items()
        }

    def add(self, inventory: Inventory) -> None:
        if inventory.product_id not in self._inventory:
            self._inventory[inventory.product_id] = 0
        self._inventory[inventory.product_id] += inventory.quantity

    def remove(self, product_id: str, quantity: int) -> None:
        if product_id in self._inventory:
            self._inventory[product_id] = max(0, self._inventory[product_id] - quantity)

    def list_all(self) -> List[Inventory]:
        from src.utils.helpers import get_products
        products = get_products()
        return [
            Inventory(
                product_id=pid, 
                quantity=qtd, 
                product_name=products[pid].name
            ) for pid, qtd in self._inventory.items()
        ]
