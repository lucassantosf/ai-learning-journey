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
    
    :param items: List of order items or a single dictionary
    :param user_id: Unique user identifier (required)
    :param customer_name: Full name of the customer (required)
    :return: Created order
    :raises ValueError: If user identification is incomplete
    """
    # Handle case where items is a single dictionary
    if isinstance(items, dict):
        items = [items]

    # Normalize and validate user identification
    if items and isinstance(items[0], dict):
        # Extract user details from first item if not provided directly
        first_item = items[0]
        user_id = user_id or first_item.get('user_id')
        customer_name = customer_name or first_item.get('customer_name')

    # Validate user identification
    if not user_id or not customer_name:
        # Try to extract from the first item if not provided
        if items and isinstance(items[0], dict):
            user_id = items[0].get('user_id', user_id)
            customer_name = items[0].get('customer_name', customer_name)

    # Final validation of user identification
    if not user_id or not customer_name:
        raise ValueError("Identificação do usuário é obrigatória. Por favor, forneça nome do cliente e ID do usuário.")

    # Normalize items if they are dictionaries
    order_items = []
    for item in items:
        # Handle both dictionary and OrderItem inputs
        if isinstance(item, dict):
            product_id = (
                product_repo.find_by_name(item.get('product_name')).id 
                if 'product_name' in item 
                else item.get('product_id')
            )
            order_items.append(
                OrderItem(
                    product_id=product_id,
                    quantity=item.get('quantity', 1)
                )
            )
        elif isinstance(item, OrderItem):
            order_items.append(item)
        else:
            raise ValueError(f"Invalid item type: {type(item)}")

    # Validate product availability and inventory
    for item in order_items:
        product = product_repo.find_by_id(item.product_id)
        if not product:
            raise ValueError(f"Produto {item.product_id} não encontrado")
        
        current_inventory = next(
            (inv for inv in inventory_repo.list_all() if inv.product_id == item.product_id), 
            None
        )
        
        if not current_inventory or current_inventory.quantity < item.quantity:
            raise ValueError(f"Estoque insuficiente para o produto {item.product_id}")
    
    # Generate order with full user identification
    order = Order(
        id=f"order_{len(order_repo.list_all()) + 1:03d}", 
        user_id=user_id,
        customer_name=customer_name,
        items=order_items, 
        creation_date=datetime.now()
    )
    order_repo.create(order)
    
    # Update inventory
    for item in order_items:
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
    products = product_repo.list_all()
    
    # Se não houver produtos, retorna uma mensagem amigável
    if not products:
        return "Não há produtos cadastrados no momento. Você pode adicionar novos produtos usando o comando 'add_product'."
    
    return products

@log_execution_time
def get_product(product_name=None, product_id=None):
    """
    Retrieve a product by name or ID
    
    :param product_name: Name of the product to find
    :param product_id: ID of the product to find
    :return: Product details or raise an informative error
    """
    products = product_repo.list_all()

    # Normalize inputs
    if product_name:
        product_name = product_name.strip("'\"")
    if product_id:
        product_id = product_id.strip("'\"")

    # Try to find by ID first
    if product_id and product_id.startswith('p'):
        product = next((p for p in products if p.id == product_id), None)
        if product:
            return product
        
    # Try to find by name (case-insensitive partial match)
    if product_name:
        matching_product = next((p for p in products if product_name.lower() in p.name.lower()), None)
        if matching_product:
            return matching_product
        
        # If no match, suggest similar products
        similar_products = [p.name for p in products if product_name.lower() in p.name.lower()]
        if similar_products:
            raise ValueError(f"Produto '{product_name}' não encontrado. Produtos similares: {', '.join(similar_products)}")
        
        raise ValueError(f"Produto '{product_name}' não encontrado")
    
    # If both name and ID are None or empty
    raise ValueError("Nome ou ID do produto deve ser fornecido")

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
    
    # Retorna apenas a mensagem de sucesso
    return f"Produto '{product.name}' adicionado com sucesso"

@log_execution_time
def update_product(product):
    # Se for um dicionário, encontrar o produto pelo nome ou ID
    if isinstance(product, dict):
        # Encontrar o produto pelo nome ou ID
        products = product_repo.list_all()
        
        # Primeiro tenta encontrar pelo ID
        if product.get('id'):
            matching_product = next((p for p in products if p.id == product.get('id')), None)
        
        # Se não encontrar pelo ID, tenta pelo nome
        if not matching_product and product.get('name'):
            matching_product = next((p for p in products if p.name == product.get('name')), None)
        
        if not matching_product:
            raise ValueError(f"Produto não encontrado. Forneça um nome ou ID válido.")
        
        # Atualizar os campos do produto existente
        if 'name' in product:
            matching_product.name = product['name']
        if 'price' in product:
            matching_product.price = product['price']
        if 'quantity' in product:
            matching_product.quantity = product['quantity']
        
        product_repo.update(matching_product)
        
        return f"Produto '{matching_product.name}' atualizado com sucesso"
    
    # Se já for um objeto Product, atualizar normalmente
    product_repo.update(product)

@log_execution_time
def delete_product(product_id: str = None):
    # Se nenhum ID for fornecido, deletar todos os produtos
    if product_id is None:
        products = product_repo.list_all()
        if not products:
            return "Não há produtos para deletar."
        
        deleted_products = []
        for product in products:
            product_repo.delete(product.id)
            deleted_products.append(product.name)
        
        return f"Todos os produtos foram deletados: {', '.join(deleted_products)}"

    # Se for passado um nome, encontrar o ID correspondente
    if not product_id.startswith('p'):
        products = product_repo.list_all()
        matching_product = next((p for p in products if p.name == product_id), None)
        
        if not matching_product:
            return f"Produto '{product_id}' não encontrado para exclusão."
        
        product_id = matching_product.id

    # Verificar se o produto existe antes de deletar
    product = product_repo.find_by_id(product_id)
    if not product:
        return f"Produto com ID {product_id} não encontrado para exclusão."

    # Realizar a exclusão
    product_repo.delete(product_id)
    return f"Produto '{product.name}' (ID: {product_id}) deletado com sucesso."

@log_execution_time
def list_inventory():
    inventories = inventory_repo.list_all()
    
    if not inventories:
        logger.info("Não há itens em estoque no momento.")
        return "Não há itens em estoque no momento."
    
    # Formatar a lista de inventário com nomes dos produtos
    inventory_list = []
    total_items = 0
    for inv in inventories:
        # Use product_name if available, otherwise skip
        if inv.product_name:
            inventory_list.append(f"🏷️ {inv.product_name} (ID: {inv.product_id}): {inv.quantity} unidades")
            total_items += inv.quantity
    
    # Log the inventory details
    logger.info(f"Listagem de estoque gerada. Total de {len(inventory_list)} produtos, {total_items} unidades em estoque.")
    
    # Adicionar informações adicionais
    summary = {
        'total_products': len(inventory_list),
        'total_items': total_items,
        'inventory_list': inventory_list,
        'formatted_summary': f"📦 Resumo do Estoque:\n" \
                             f"Total de Produtos: {len(inventory_list)}\n" \
                             f"Total de Unidades: {total_items}\n\n" \
                             f"Detalhes do Estoque:\n" + "\n".join(inventory_list)
    }
    
    return summary

@log_execution_time
def update_inventory(product_name: str = None, quantity: int = None, inventory: dict = None):
    """
    Update inventory for a product 
    
    :param product_name: Exact name of the product
    :param quantity: Quantity to add to the inventory
    :param inventory: Alternative input as a dictionary
    :return: Success message or error description
    """
    # Handle dictionary input if provided
    if inventory and isinstance(inventory, dict):
        product_id = inventory.get('product_id')
        quantity = inventory.get('quantity')
        
        # Find the product by ID
        product = product_repo.find_by_id(product_id)
        if not product:
            return f"Produto com ID {product_id} não encontrado."
        
        product_name = product.name

    # Validate input parameters
    if not product_name or quantity is None:
        return "Por favor, forneça o nome do produto e a quantidade a ser adicionada."

    # Find the product by exact name if not found via ID
    if not product:
        products = product_repo.list_all()
        product = next((p for p in products if p.name == product_name), None)

    if not product:
        return f"Produto '{product_name}' não encontrado."

    # Create Inventory object with the product's ID
    inventory_obj = Inventory(
        product_id=product.id, 
        quantity=quantity
    )

    # Add to inventory
    inventory_repo.add(inventory_obj)

    # Log the inventory update
    logger.info(f"Estoque do produto '{product_name}' atualizado: +{quantity} unidades")

    return f"Adicionadas {quantity} unidades ao estoque do produto '{product_name}'"
