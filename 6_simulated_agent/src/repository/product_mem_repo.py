from typing import Dict, List, Optional
from src.repository.interfaces.product_repository import ProductRepository
from src.models.product import Product
from src.models.inventory import Inventory
from src.repository.inventory_mem_repo import InventoryMemRepository

class ProductMemRepository(ProductRepository):
    def __init__(self, products: Dict[str, Product], inventory: Optional[InventoryMemRepository] = None):
        self._products = products
        self._inventory_repo = inventory  # deve ser passado!

    def _attach_inventory(self, product: Product) -> Optional[Product]:
        """Return a copy of the product with *quantity* refletindo o inventory atual."""
        if not product:
            return None
        prod_copy = Product(
            id=product.id,
            name=product.name,
            price=product.price,
            average_rating=product.average_rating,
            image_url=product.image_url
        )
        # Se houver repo de inventory, traz a quantidade atual e coloca no campo quantity do Product
        quantity = self._inventory_repo.get_quantity(product.id) if self._inventory_repo else 0
        prod_copy.quantity = quantity

        # (Opcional) também manter um objeto Inventory acoplado, se você quiser usar em outros pontos
        # Só vai aparecer no repr se seu dataclass Product tiver esse campo declarado.
        # prod_copy.inventory = Inventory(product_id=product.id, quantity=quantity, product_name=product.name)

        return prod_copy

    def list_all(self) -> List[Product]:
        return [self._attach_inventory(p) for p in self._products.values()]

    def find_by_id(self, product_id: str) -> Optional[Product]:
        return self._attach_inventory(self._products.get(product_id))

    def create(self, product: Product) -> Product:
        self._products[product.id] = product
        return self._attach_inventory(product)

    def update(self, product: Product) -> None:
        # Armazena os campos "de verdade"; quantity é derivado do inventory, então não persista quantity aqui.
        if product.id in self._products:
            base = self._products[product.id]
            base.name = product.name
            base.price = product.price
            base.average_rating = product.average_rating
            base.image_url = product.image_url

    def delete(self, product_id: str) -> None:
        if product_id in self._products:
            del self._products[product_id]

    def find_by_name(self, product_name: str) -> Optional[Product]:
        for product in self._products.values():
            if product.name.lower() == product_name.lower():
                return self._attach_inventory(product)
        return None

    # 👇 Helpers públicos para não acessar atributos "privados" de fora
    def add_inventory(self, product_id: str, quantity: int) -> None:
        if not self._inventory_repo:
            raise RuntimeError("Inventory repository not configured")
        self._inventory_repo.add(Inventory(product_id=product_id, quantity=quantity))

    def remove_inventory(self, product_id: str, quantity: int) -> None:
        if not self._inventory_repo:
            raise RuntimeError("Inventory repository not configured")
        self._inventory_repo.remove(product_id, quantity)

    def get_quantity(self, product_id: str) -> int:
        if not self._inventory_repo:
            return 0
        return self._inventory_repo.get_quantity(product_id)
