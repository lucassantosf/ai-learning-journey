import re
from dataclasses import dataclass
from datetime import datetime
from src.models.order import Order, OrderItem
from src.models.product import Product
from src.models.inventory import Inventory
from typing import List, Optional
from src.utils.logger import setup_logger, log_execution_time

# Inicializa logger
logger = setup_logger()

# Repositórios em memória ou SQLite
from src.repository.product_mem_repo import ProductMemRepository
from src.repository.order_mem_repo import OrderMemRepository
from src.repository.inventory_mem_repo import InventoryMemRepository

from src.repository.sqlite_product_repo import SQLiteProductRepository
from src.repository.sqlite_order_repo import SQLiteOrderRepository
from src.repository.sqlite_inventory_repo import SQLiteInventoryRepository

# Usar repositórios SQLite por padrão
product_repo = SQLiteProductRepository()
order_repo = SQLiteOrderRepository()
inventory_repo = SQLiteInventoryRepository()

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
        user_id = user_id or first_item.get('user_id') or first_item.get('cpf')
        customer_name = customer_name or first_item.get('customer_name') or first_item.get('name')

    # Attempt to extract user details from various possible sources
    if not user_id:
        # Try to find user_id in various formats
        user_id = (
            first_item.get('user_id') or 
            first_item.get('cpf') or 
            first_item.get('id') or 
            first_item.get('customer_id')
        )

    if not customer_name:
        # Try to find customer_name in various formats
        customer_name = (
            first_item.get('customer_name') or 
            first_item.get('name') or 
            first_item.get('full_name')
        )

    # Normalize customer name to title case
    if customer_name:
        customer_name = customer_name.title()

    # Final validation of user identification
    if not user_id or not customer_name:
        raise ValueError(
            "Identificação do usuário é obrigatória. " 
            "Por favor, forneça nome do cliente e ID do usuário. " 
            "Detalhes fornecidos: " + str(first_item)
        )

    # Normalize items if they are dictionaries
    order_items = []
    for item in items:
        # Handle both dictionary and OrderItem inputs
        if isinstance(item, dict):
            # Find product by name or ID
            product_search = item.get('product_name') or item.get('product_id')
            if product_search:
                try:
                    product = get_product(product_name=product_search)
                    product_id = product.id
                except ValueError:
                    # If product not found, try to add it
                    try:
                        add_product(product={'name': product_search, 'price': 50.00, 'quantity': 20})
                        product = get_product(product_name=product_search)
                        product_id = product.id
                    except Exception as e:
                        raise ValueError(f"Não foi possível encontrar ou adicionar o produto: {e}")
            else:
                raise ValueError("Produto não especificado no item do pedido")
            
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
    
    # Se products for uma string (sem produtos), retorna lista vazia
    if isinstance(products, str):
        return []
    
    # Se não houver produtos, retorna lista vazia
    if not products:
        return []
    
    # Retornar lista de produtos
    return products

@log_execution_time
def format_products_list(products):
    """
    Formata a lista de produtos para exibição amigável
    
    :param products: Lista de objetos Product
    :return: String formatada com detalhes dos produtos
    """
    # Se a lista estiver vazia, retorna mensagem amigável
    if not products:
        return "Não há produtos cadastrados no momento. Você pode adicionar novos produtos usando o comando 'add_product'."
    
    # Formatar lista de produtos de forma amigável
    formatted_products = []
    for product in products:
        formatted_product = (
            f"🏷️ {product.name}: "
            f"R${product.price:.2f}, "
            f"Avaliação: {product.average_rating} "
            f"(Quantidade: {product.quantity})"
        )
        formatted_products.append(formatted_product)
    
    # Criar uma string formatada para exibição
    return "\n".join(formatted_products)

@log_execution_time
def get_product(product_name=None, product_id=None):
    # Aggressive cleaning of product name
    def clean_name(name):
        if name is None:
            return None
        # Remove quotes, extra whitespace, and normalize
        return re.sub(r'["\'\(\)]', '', str(name)).strip().lower()

    # Normalize inputs
    clean_product_name = clean_name(product_name)
    clean_product_id = clean_name(product_id)

    # If product_id looks like a product name, treat it as such
    if clean_product_id and not clean_product_id.startswith('p'):
        clean_product_name = clean_product_id
        clean_product_id = None

    # Get all products
    products = product_repo.list_all()

    # Try to find by ID first
    if clean_product_id and clean_product_id.startswith('p'):
        product = next((p for p in products if p.id == clean_product_id), None)
        if product:
            return product
        
    # Try to find by name
    if clean_product_name:
        # Exact match
        exact_match = next((p for p in products if clean_name(p.name) == clean_product_name), None)
        if exact_match:
            return exact_match
        
        # Partial match
        partial_match = next((p for p in products if clean_product_name in clean_name(p.name)), None)
        if partial_match:
            return partial_match
        
        # If no match, provide helpful error
        similar_products = [p.name for p in products if clean_product_name in clean_name(p.name)]
        if similar_products:
            raise ValueError(f"Produto '{product_name}' não encontrado. Produtos similares: {', '.join(similar_products)}")
        
        raise ValueError(f"Produto '{product_name}' não encontrado")
    
    raise ValueError("Nome ou ID do produto deve ser fornecido")

@log_execution_time
def add_product(product=None, **kwargs):
    # Handle different input formats
    if product is None:
        product = kwargs
    
    # If product is a string, assume it's the name
    if isinstance(product, str):
        product = {'name': product}
    
    # Convert dictionary to Product if needed
    if isinstance(product, dict):
        # Normalize keys to lowercase
        product = {k.lower(): v for k, v in product.items()}
        
        # Handle different possible key names
        name = product.get('name') or product.get('product') or product.get('nome')
        price = product.get('price') or product.get('preco') or product.get('valor')
        quantity = product.get('quantity', 0) or product.get('quantidade', 0)
        
        product = Product(
            name=name,
            price=price,
            quantity=quantity
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
        # Try to get product ID or name from the dictionary
        product_id = inventory.get('product_id')
        product_name = inventory.get('product_name')
        quantity = inventory.get('quantity')
        
        # If product_id is not a valid ID (starts with 'p'), treat it as product name
        if product_id and not str(product_id).startswith('p'):
            product_name = product_id
            product_id = None

    # Validate input parameters
    if not product_name and not product_id:
        return "Por favor, forneça o nome ou ID do produto e a quantidade a ser adicionada."
    
    if quantity is None:
        return "Por favor, forneça a quantidade a ser adicionada."

    # Find the product
    if product_id:
        product = product_repo.find_by_id(product_id)
    else:
        products = product_repo.list_all()
        product = next((p for p in products if p.name == product_name), None)

    if not product:
        return f"Produto '{product_name or product_id}' não encontrado."

    # Create Inventory object with the product's ID
    inventory_obj = Inventory(
        product_id=product.id, 
        quantity=quantity
    )

    # Add to inventory
    inventory_repo.add(inventory_obj)

    # Log the inventory update
    logger.info(f"Estoque do produto '{product.name}' atualizado: +{quantity} unidades")

    return f"Adicionadas {quantity} unidades ao estoque do produto '{product.name}'"
