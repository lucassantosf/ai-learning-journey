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
def generate_order(items, user_id=None, customer_name=None):
    """
    Generate a new order with given items
    
    :param items: List of order items
    :param user_id: Unique user identifier (required)
    :param customer_name: Full name of the customer (required)
    :return: Created order
    :raises ValueError: If user identification is incomplete
    """
    # Validate user identification
    if not user_id or not customer_name:
        raise ValueError("User identification is required. Please provide both user_id and customer_name.")

    # Validate product availability and inventory
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
    
    # Generate order with full user identification
    order = Order(
        id=f"order_{len(order_repo.list_all()) + 1:03d}", 
        user_id=user_id,
        customer_name=customer_name,
        items=items, 
        creation_date=datetime.now()
    )
    order_repo.create(order)
    
    # Update inventory
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
def add_product(product):
    # Convert dictionary to Product if needed
    if isinstance(product, dict):
        product = Product(
            name=product.get('name'),
            price=product.get('price'),
            quantity=product.get('quantity', 0)
        )
    
    # Validate required fields
    if not product.name:
        raise ValueError("Nome do produto é obrigatório")
    if product.price is None or product.price < 0:
        raise ValueError("Preço do produto deve ser um número não negativo")
    if product.quantity is None or product.quantity < 0:
        raise ValueError("Quantidade do produto deve ser um número não negativo")
    
    # Create the product
    product_repo.create(product)
    
    # Log the product addition
    logger.info(f"Produto adicionado: {product.name}")
    
    return f"Produto '{product.name}' adicionado com sucesso"

@log_execution_time
def update_product(product):
    # Se for um dicionário, encontrar o produto pelo nome
    if isinstance(product, dict):
        # Encontrar o produto pelo nome
        products = product_repo.list_all()
        matching_product = next((p for p in products if p.name == product.get('name')), None)
        
        if not matching_product:
            raise ValueError(f"Produto com nome '{product.get('name')}' não encontrado")
        
        # Atualizar os campos do produto existente
        matching_product.price = product.get('price', matching_product.price)
        matching_product.quantity = product.get('quantity', matching_product.quantity)
        
        product_repo.update(matching_product)
        
        return f"Produto '{matching_product.name}' atualizado com sucesso"
    
    # Se já for um objeto Product, atualizar normalmente
    product_repo.update(product)

@log_execution_time
def delete_product(product_id: str):
    product_repo.delete(product_id)

@log_execution_time
def update_inventory(inventory: Inventory):
    inventory_repo.add(inventory)
