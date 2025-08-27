import re
import ast
import uuid
from datetime import datetime
from datetime import datetime
from src.models.product import Product
from src.models.inventory import Inventory
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
def generate_order(items):
    """
    Gera um pedido com base nos itens passados.
    Aceita:
      - Lista de dicts
      - Um único dict
      - String representando dict/list (vinda do modelo)
    """

    # Se vier string, tenta converter
    if isinstance(items, str):
        try:
            items = ast.literal_eval(items)  # converte string para objeto Python
        except Exception:
            raise ValueError(f"❌ items inválido (não pôde ser convertido): {items}")

    # Se for dict único, transforma em lista
    if isinstance(items, dict):
        items = [items]

    if not isinstance(items, list):
        raise ValueError("❌ items deve ser lista de dicionários")

    order = {
        "order_id": str(uuid.uuid4()),
        "customer_name": None,
        "user_id": None,
        "items": [],
        "total": 0.0,
        "created_at": datetime.now().isoformat()
    }

    for item in items:
        if not isinstance(item, dict):
            raise ValueError(f"❌ Item inválido: {item}. Esperado dict.")

        product_name = item.get("product_name")
        quantity = item.get("quantity", 1)
        customer_name = item.get("customer_name")
        user_id = item.get("user_id")

        # Busca produto
        product = get_product(product_name)
        if not product:
            raise ValueError(f"❌ Produto '{product_name}' não encontrado.")

        # Atualiza dados do pedido
        order["customer_name"] = customer_name
        order["user_id"] = user_id
        order["items"].append({
            "product_name": product.name,
            "quantity": quantity,
            "unit_price": product.price,
            "subtotal": product.price * quantity
        })
        order["total"] += product.price * quantity

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
def add_product(name, price):

    # Converte para float (ou int, se quiser somente valores inteiros)
    try:
        price = float(price)
    except ValueError:
        raise ValueError("Preço do produto deve ser numérico")
    
    product = Product(
        name=name,
        price=price,
        quantity=0
    )
    
    # Validate required fields
    if not name:
        raise ValueError("Nome do produto é obrigatório")
    if not price or price < 0:
        raise ValueError("Preço do produto deve ser um número não negativo")
    
    # Create the product
    product_repo.create(product)
    
    # Log the product addition
    logger.info(f"Produto adicionado: {product.name}")
    
    # Retorna apenas a mensagem de sucesso
    return f"Produto '{product.name}' adicionado com sucesso"

@log_execution_time
def update_product(product_id, **kwargs):
    """
    Atualiza um produto existente na base.
    """
    products = product_repo.list_all()
    
    # Encontra o produto pelo ID.
    # Usamos o `product_id` que já foi passado como argumento.
    matching_product = next((p for p in products if p.id == product_id), None)
    
    # Se não encontrar, lança o erro.
    if not matching_product:
        raise ValueError("Produto não encontrado. Forneça um ID válido.")
    
    # Atualiza os campos existentes a partir de kwargs
    if "name" in kwargs:
        matching_product.name = kwargs["name"]
    if "price" in kwargs:
        # Garante que o preço seja float antes de atribuir
        try:
            matching_product.price = float(kwargs["price"])
        except ValueError:
            raise ValueError("Preço inválido")
    if "quantity" in kwargs:
        matching_product.quantity = kwargs["quantity"]
    if "average_rating" in kwargs:
        matching_product.average_rating = kwargs["average_rating"]
    if "image_url" in kwargs:
        matching_product.image_url = kwargs["image_url"]
    
    # Persiste a mudança.
    product_repo.update(matching_product)
    
    return f"Produto '{matching_product.name}' atualizado com sucesso"

@log_execution_time
def delete_product(product_id: str = None):
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
def update_inventory(product_id: str = None, method: str = None, quantity = None):
    """
    Update inventory for a product 
    
    :param product_id: Product ID to update
    :param quantity: Quantity to add/remove to the inventory
    :return: Success message or error description
    """
    # Find the product
    if product_id:
        product = product_repo.find_by_id(product_id)
    else:
        products = product_repo.list_all()
        product = next((p for p in products if p.name == product_id), None)

    if not product:
        return f"Produto '{product_id}' não encontrado."

    if method not in ['add', 'remove']:
        return "Ação inválida. Use 'add' para adicionar ou 'remove' para remover estoque."
    
    # 1. Validação do parâmetro 'quantity'
    if quantity is None:
        return "A quantidade não pode ser vazia. Por favor, forneça um número."

    # 2. Tentativa de conversão para inteiro e tratamento de erro
    try:
        # Tenta converter o valor (que pode ser string ou int) para um inteiro
        quantity = int(quantity)
    except (ValueError, TypeError):
        # Captura erros se a conversão falhar (ex: 'dez', '10.5', etc.)
        return "Quantidade inválida. Por favor, forneça um número inteiro para a quantidade."
        
    if method == 'remove':
        inventory_repo.remove(product_id=product.id, quantity=quantity)
    else:
        inventory_repo.add(Inventory(product_id=product.id, quantity=quantity))
   
    # Log the inventory update
    logger.info(f"Estoque do produto '{product.name}' atualizado: {method} {quantity} unidades")

    return f"Estoque do produto '{product.name}' atualizado: {method} {quantity} unidades"