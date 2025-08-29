from typing import Dict, List
from src.repository.interfaces.inventory_repository import InventoryRepository
from src.models.inventory import Inventory

class InventoryMemRepository(InventoryRepository):
    def __init__(self, products: dict):
        self._products = products
        self._inventory: Dict[str, int] = {pid: 0 for pid in products.keys()}

    def get_quantity(self, product_id: str) -> int:
        return self._inventory.get(product_id, 0)
    
    def add(self, inventory: Inventory) -> None:
        from src.models.product import Product
        
        if inventory.product_id not in self._products:
            temp_product = Product(
                id=inventory.product_id, 
                name=f"Temporary Product ({inventory.product_id})", 
                price=0
            )
            self._products[inventory.product_id] = temp_product

        self._inventory[inventory.product_id] = self._inventory.get(inventory.product_id, 0) + inventory.quantity

    def remove(self, product_id: str, quantity: int) -> None:
        current = self._inventory.get(product_id, 0)
        if quantity < 0:
            raise ValueError("Quantity to remove must be >= 0")
        if current < quantity:
            raise ValueError(f"Insufficient inventory for product {product_id}: have {current}, need {quantity}")
        self._inventory[product_id] = current - quantity

    def list_all(self) -> List[Inventory]:
        return [
            Inventory(
                product_id=pid,
                quantity=qtd,
                product_name=self._products[pid].name if pid in self._products else f"Unknown Product ({pid})"
            )
            for pid, qtd in self._inventory.items()
        ]