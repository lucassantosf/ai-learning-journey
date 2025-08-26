from typing import Dict, List
import uuid
from src.repository.interfaces.product_repository import ProductRepository
from src.models.product import Product
from src.utils.helpers import get_products
from src.repository.inventory_mem_repo import InventoryMemRepository

class ProductMemRepository(ProductRepository):
    def __init__(self, products: Dict[str, Product], inventory: Dict[str, int]):
        self._products = products
        self._inventory = inventory

    def list_all(self) -> List[Product]:
        product_list = []
        for pid, product in self._products.items():
            prod_copy = Product(
                id=product.id,
                name=product.name,
                price=product.price,
                average_rating=product.average_rating,
                image_url=product.image_url
            )
            prod_copy.quantity = self._inventory.get(pid, 0)
            product_list.append(prod_copy)
        return product_list

    def find_by_id(self, product_id: str) -> Product:
        return self._products.get(product_id)

    def create(self, product: Product) -> Product:
        self._products[product.id] = product
        return product

    def update(self, product: Product) -> None:
        if product.id in self._products:
            self._products[product.id] = product

    def delete(self, product_id: str) -> None:
        if product_id in self._products:
            del self._products[product_id]

    def find_by_name(self, product_name: str) -> Product:
        """
        Find a product by its exact name (case-insensitive)
        
        :param product_name: Name of the product to find
        :return: Product if found, None otherwise
        """
        for product in self._products.values():
            if product.name.lower() == product_name.lower():
                return product
        return None
