from typing import Dict, List
from src.repository.interfaces.order_repository import OrderRepository
from src.models.order import Order
from datetime import datetime

class OrderMemRepository(OrderRepository):
    def __init__(self):
        self._orders: Dict[str, Order] = {}

    def list_all(self) -> List[Order]:
        return list(self._orders.values())

    def find_by_id(self, order_id: str) -> Order:
        return self._orders.get(order_id)

    def create(self, order: Order) -> None:
        self._orders[order.id] = order

    def rate(self, order_id: str, rating: float) -> None:
        if order_id in self._orders:
            self._orders[order_id].rating = rating
