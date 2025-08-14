from typing import Dict, List
from src.repository.interfaces.inventory_repository import InventoryRepository
from src.models.inventory import Inventory

class InventoryMemRepository(InventoryRepository):
    def __init__(self):
        from src.utils.helpers import get_products
        self._products = get_products()
        self._inventory: Dict[str, int] = {
            product_id: product.quantity 
            for product_id, product in self._products.items()
        }

    def add(self, inventory: Inventory) -> None:
        from src.models.product import Product
        
        # If product doesn't exist in products, create a temporary product
        if inventory.product_id not in self._products:
            temp_product = Product(
                id=inventory.product_id, 
                name=f"Temporary Product ({inventory.product_id})", 
                price=0, 
                quantity=0
            )
            self._products[inventory.product_id] = temp_product

        # Add to inventory
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
                product_name=products.get(pid, None).name if products.get(pid, None) else f"Unknown Product ({pid})"
            ) for pid, qtd in self._inventory.items()
        ]
