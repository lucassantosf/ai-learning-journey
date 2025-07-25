from abc import ABC, abstractmethod
from typing import List
from src.models.inventory import Inventory

class InventoryRepository(ABC):
    @abstractmethod
    def add(self, inventory: Inventory) -> None:
        pass

    @abstractmethod
    def remove(self, product_id: str, quantity: int) -> None:
        pass

    @abstractmethod
    def list_all(self) -> List[Inventory]:
        pass
