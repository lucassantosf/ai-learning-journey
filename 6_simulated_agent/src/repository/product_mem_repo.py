from typing import Dict, List
from src.repository.interfaces.product_repository import ProductRepository
from src.models.product import Product
from src.models.inventory import Inventory
from src.repository.inventory_mem_repo import InventoryMemRepository

class ProductMemRepository(ProductRepository):
    def __init__(self, products: Dict[str, Product], inventory= None):
        self._products = products
        self._inventory_repo = inventory

    def _attach_inventory(self, product: Product) -> Product:
        """Return a copy of the product with inventory attached"""
        if not product:
            return None
        prod_copy = Product(
            id=product.id,
            name=product.name,
            price=product.price,
            average_rating=product.average_rating,
            image_url=product.image_url
        )
        # Pega quantidade atual no repo de inventory
        quantity = self._inventory_repo.get_quantity(product.id)

        # Cria objeto Inventory e cola no produto
        prod_copy.inventory = Inventory(
            product_id=product.id,
            quantity=quantity,
            product_name=product.name
        )
        return prod_copy

    def list_all(self) -> List[Product]:
        return [self._attach_inventory(p) for p in self._products.values()]

    def find_by_id(self, product_id: str) -> Product:
        return self._attach_inventory(self._products.get(product_id))

    def create(self, product: Product) -> Product:
        self._products[product.id] = product
        return self._attach_inventory(product)

    def update(self, product: Product) -> None:
        if product.id in self._products:
            self._products[product.id] = product

    def delete(self, product_id: str) -> None:
        if product_id in self._products:
            del self._products[product_id]

    def find_by_name(self, product_name: str) -> Product:
        for product in self._products.values():
            if product.name.lower() == product_name.lower():
                return self._attach_inventory(product)
        return None