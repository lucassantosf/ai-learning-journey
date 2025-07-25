from abc import ABC, abstractmethod
from typing import List
from src.models.order import Order

class OrderRepository(ABC):
    @abstractmethod
    def list_all(self) -> List[Order]:
        pass

    @abstractmethod
    def find_by_id(self, order_id: str) -> Order:
        pass

    @abstractmethod
    def create(self, order: Order) -> None:
        pass

    @abstractmethod
    def rate(self, order_id: str, rating: float) -> None:
        pass
