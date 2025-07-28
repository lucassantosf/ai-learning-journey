from dataclasses import dataclass
from datetime import datetime
from src.repository.product_mem_repo import ProductMemRepository
from src.repository.order_mem_repo import OrderMemRepository
from src.repository.inventory_mem_repo import InventoryMemRepository
from src.models.order import Order, OrderItem
from src.models.product import Product
from src.models.inventory import Inventory
from typing import List, Optional

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
    # Validate inventory before creating order
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
    
    # Create order
    order = Order(
        id=f"order_{len(order_repo.list_all()) + 1:03d}", 
        items=items, 
        creation_date=datetime.now(),
        customer_id=customer_id
    )
    order_repo.create(order)
    
    # Update inventory
    for item in items:
        inventory_repo.remove(item.product_id, item.quantity)
    
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

def list_products():
    """
    List all available products
    
    :return: List of all products
    """
    return product_repo.list_all()

def get_product(product_id):
    """
    Retrieve a product by its ID
    
    :param product_id: Unique identifier for the product
    :return: Product details
    """
    return product_repo.find_by_id(product_id)

def list_inventory():
    """
    List current inventory levels
    
    :return: List of inventory items
    """
    return inventory_repo.list_all()

def add_product(product: Product):
    """
    Add a new product to the repository
    
    :param product: Product to be added
    """
    product_repo.create(product)

def update_product(product: Product):
    """
    Update an existing product
    
    :param product: Product with updated information
    """
    product_repo.update(product)

def delete_product(product_id: str):
    """
    Delete a product from the repository
    
    :param product_id: Unique identifier of the product to delete
    """
    product_repo.delete(product_id)

def update_inventory(inventory: Inventory):
    """
    Update inventory for a specific product
    
    :param inventory: Inventory item to update
    """
    inventory_repo.add(inventory)
