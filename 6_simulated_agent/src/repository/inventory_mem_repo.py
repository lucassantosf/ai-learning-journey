from typing import Dict, List
from src.repository.interfaces.inventory_repository import InventoryRepository
from src.models.inventory import Inventory

class InventoryMemRepository(InventoryRepository):
    def __init__(self):
        self._inventory: Dict[str, int] = {}

    def add(self, inventory: Inventory) -> None:
        if inventory.product_id not in self._inventory:
            self._inventory[inventory.product_id] = 0
        self._inventory[inventory.product_id] += inventory.quantity

    def remove(self, product_id: str, quantity: int) -> None:
        if product_id in self._inventory:
            self._inventory[product_id] = max(0, self._inventory[product_id] - quantity)

    def list_all(self) -> List[Inventory]:
        return [Inventory(product_id=pid, quantity=qtd) for pid, qtd in self._inventory.items()]
