from dataclasses import dataclass
from datetime import datetime
from src.repository.product_mem_repo import ProductMemRepository
from src.repository.order_mem_repo import OrderMemRepository
from src.repository.inventory_mem_repo import InventoryMemRepository
from src.models.order import Order, OrderItem
from src.models.product import Product
from src.models.inventory import Inventory
from typing import List, Optional
from src.utils.logger import setup_logger, log_execution_time

# Inicializa logger
logger = setup_logger()

# Repositórios em memória
product_repo = ProductMemRepository()
order_repo = OrderMemRepository()
inventory_repo = InventoryMemRepository()

@log_execution_time
def generate_order(items, customer_id=None):
    """
    Generate a new order with given items
    
    :param items: List of order items
    :param customer_id: Optional customer identifier
    :return: Created order
    """
    for item in items:
        product = product_repo.find_by_id(item.product_id)
        if not product:
            raise ValueError(f"Product {item.product_id} not found")
        
        current_inventory = next(
            (inv for inv in inventory_repo.list_all() if inv.product_id == item.product_id), 
            None
        )
        
        if not current_inventory or current_inventory.quantity < item.quantity:
            raise ValueError(f"Insufficient inventory for product {item.product_id}")
    
    order = Order(
        id=f"order_{len(order_repo.list_all()) + 1:03d}", 
        items=items, 
        creation_date=datetime.now(),
        customer_id=customer_id
    )
    order_repo.create(order)
    
    for item in items:
        inventory_repo.remove(item.product_id, item.quantity)
    
    return order

@log_execution_time
def get_order(order_id):
    return order_repo.find_by_id(order_id)

@log_execution_time
def list_orders():
    return order_repo.list_all()

@log_execution_time
def rate_order(order_id, rating):
    order_repo.rate(order_id, rating)

@log_execution_time
def list_products():
    return product_repo.list_all()

@log_execution_time
def get_product(product_id):
    return product_repo.find_by_id(product_id)

@log_execution_time
def list_inventory():
    return inventory_repo.list_all()

@log_execution_time
def add_product(product: Product):
    product_repo.create(product)

@log_execution_time
def update_product(product: Product):
    product_repo.update(product)

@log_execution_time
def delete_product(product_id: str):
    product_repo.delete(product_id)

@log_execution_time
def update_inventory(inventory: Inventory):
    inventory_repo.add(inventory)
