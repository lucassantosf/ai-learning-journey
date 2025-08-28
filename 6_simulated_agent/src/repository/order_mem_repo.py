from typing import Dict, List
from src.repository.interfaces.order_repository import OrderRepository
from src.repository.product_mem_repo import ProductMemRepository
from src.models.order import Order

class OrderMemRepository(OrderRepository):
    def __init__(self, product_repo: ProductMemRepository):
        self._orders: Dict[str, Order] = {}
        self._product_repo = product_repo
        
    def list_all(self) -> List[Order]:
        return list(self._orders.values())

    def find_by_id(self, order_id: str) -> Order:
        return self._orders.get(order_id)

    def create(self, order: Order) -> None:
        # percorre os itens do pedido
        for item in order.items:
            product = self._product_repo.find_by_id(item.product_id)
            if not product:
                raise ValueError(f"Product {item.product_id} not found")

            if product.inventory.quantity < item.quantity:
                raise ValueError(f"Insufficient inventory for product {item.product_id}")

            # debita o estoque
            product.inventory.quantity -= item.quantity
            self._product_repo.update(product)

        # salva o pedido em memória
        self._orders[order.id] = order
        return order

    def rate(self, order_id: str, rating: float) -> None:
        if order_id in self._orders:
            order = self._orders[order_id]
            order.rating = rating

            # Atualiza a média dos produtos do pedido
            for item in order.items:
                product = self._product_repo.find_by_id(item.product_id)
                if product:
                    # Exemplo simples: média ponderada incremental
                    if product.average_rating is None:
                        product.average_rating = rating
                    else:
                        product.average_rating = (product.average_rating + rating) / 2
                    
                    self._product_repo.update(product)