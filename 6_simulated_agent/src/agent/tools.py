from dataclasses import dataclass
from src.repository.product_mem_repo import ProductMemRepository
from src.repository.order_mem_repo import OrderMemRepository
from src.repository.inventory_mem_repo import InventoryMemRepository
from src.models.order import Order, OrderItem
from src.models.product import Product

product_repo = ProductMemRepository()
order_repo = OrderMemRepository()
inventory_repo = InventoryMemRepository()

def generate_order(items, customer_id=None):
    """
    Generate a new order with given items
    
    :param items: List of order items
    :param customer_id: Optional customer identifier
    :return: Created order
    """
    # Implementation would depend on specific business logic
    order = Order(
        id=f"order_{len(order_repo.list_all()) + 1:03d}", 
        items=items, 
        creation_date=datetime.now()
    )
    order_repo.create(order)
    return order

def get_order(order_id):
    """
    Retrieve an order by its ID
    
    :param order_id: Unique identifier for the order
    :return: Order details
    """
    return order_repo.find_by_id(order_id)

def list_orders():
    """
    List all existing orders
    
    :return: List of all orders
    """
    return order_repo.list_all()

def rate_order(order_id, rating):
    """
    Rate an existing order
    
    :param order_id: Unique identifier for the order
    :param rating: Rating to assign to the order
    """
    order_repo.rate(order_id, rating)
