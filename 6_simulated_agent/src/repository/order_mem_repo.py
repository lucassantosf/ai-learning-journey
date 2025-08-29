from typing import Dict, List, Optional
from src.repository.interfaces.order_repository import OrderRepository
from src.repository.product_mem_repo import ProductMemRepository
from src.models.order import Order

class OrderMemRepository(OrderRepository):
    def __init__(self, product_repo: ProductMemRepository):
        self._orders: Dict[str, Order] = {}
        self._product_repo = product_repo
        
    def list_all(self) -> List[Order]:
        return list(self._orders.values())

    def find_by_id(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def create(self, order: Order) -> Order:
        # validação de estoque e débito efetivo no InventoryRepo
        for item in order.items:
            available = self._product_repo.get_quantity(item.product_id)
            if available < item.quantity:
                raise ValueError(f"Insufficient inventory for product {item.product_id}: have {available}, need {item.quantity}")
            self._product_repo.remove_inventory(item.product_id, item.quantity)

        self._orders[order.id] = order
        return order

    def rate(self, order_id: str, rating: float) -> None:
        if order_id in self._orders:
            order = self._orders[order_id]
            order.rating = rating

            for item in order.items:
                product = self._product_repo.find_by_id(item.product_id)  # cópia com quantity atualizado
                if product:
                    # média simples incremental (exemplo)
                    if product.average_rating is None:
                        product.average_rating = rating
                    else:
                        product.average_rating = (product.average_rating + rating) / 2
                    # persistir de volta no storage real do produto (sem quantity)
                    self._product_repo.update(product)
