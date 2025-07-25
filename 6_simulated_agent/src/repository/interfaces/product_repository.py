from abc import ABC, abstractmethod
from typing import List
from src.models.product import Product

class ProductRepository(ABC):
    @abstractmethod
    def list_all(self) -> List[Product]:
        pass

    @abstractmethod
    def find_by_id(self, product_id: str) -> Product:
        pass

    @abstractmethod
    def create(self, product: Product) -> None:
        pass

    @abstractmethod
    def update(self, product: Product) -> None:
        pass

    @abstractmethod
    def delete(self, product_id: str) -> None:
        pass
