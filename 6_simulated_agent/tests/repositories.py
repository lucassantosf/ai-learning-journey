from datetime import datetime
from pprint import pprint
from src.repository.sqlite_base import db
from sqlalchemy import text

from src.repository.product_mem_repo import ProductMemRepository
from src.repository.order_mem_repo import OrderMemRepository
from src.repository.inventory_mem_repo import InventoryMemRepository

from src.repository.sqlite_product_repo import SQLiteProductRepository
from src.repository.sqlite_order_repo import SQLiteOrderRepository
from src.repository.sqlite_inventory_repo import SQLiteInventoryRepository

from src.models.product import Product
from src.models.order import Order, OrderItem
from src.models.inventory import Inventory

from src.repository.sqlite_models import ProductModel, OrderModel, OrderItemModel, InventoryModel
from src.utils.helpers import get_products

def test_memory_repositories():
    print("🔍 Testing In-Memory Repositories")
    # Initialize repositories
    products=get_products()
    inventory_repo = InventoryMemRepository(products)
    product_repo = ProductMemRepository(products=products, inventory=inventory_repo)
    product_repo._inventory = inventory_repo._inventory  # conecta os dois
    order_repo = OrderMemRepository(product_repo)

    print("✅ Available Products:")
    product_list = product_repo.list_all()
    pprint(product_list)
    print("\n")

    # Test: Create new product
    new_product = Product(name="RGB Gaming Headset", price=150)
    product = product_repo.create(new_product)
    print("➕ Product Created:")
    pprint(product_repo.find_by_id(product.id))
    print("\n")

    # Test: Update product
    product_to_update = product_repo.find_by_id(product.id)
    product_to_update.name = f"{product_to_update.name} - Updated"
    product_repo.update(product_to_update)
    print("✏️ Product Updated (name):")
    pprint(product_repo.find_by_id(product.id))
    print("\n")

    # Test: Add inventory
    inventory_repo.add(Inventory(product_id=product.id, quantity=5))
    print("➕ Inventory after adding 5 units:")
    pprint(inventory_repo.list_all())
    print("\n")

    # Test: Remove inventory
    inventory_repo.remove(product_id=product.id, quantity=3)
    print("➖ Inventory after removing 3 units:")
    pprint(inventory_repo.list_all())
    print("\n")

    # Test: Create order
    items = [OrderItem(product_id=product.id, quantity=1), OrderItem(product_id=product_list[1].id, quantity=2)]
    new_order = Order(
        customer_document="test_user", 
        customer_name="Test Customer", 
        items=items
    )
    order_repo.create(new_order)
    print("📦 Order Created:")
    pprint(order_repo.find_by_id(new_order.id))
    print("\n")

    # Test: Rate order
    print(f"Product before rated ({product.id}):")
    pprint(product_repo.find_by_id(product.id))

    order_repo.rate(new_order.id, 1.0)
    print("🌟 Order Rated:")
    pprint(order_repo.find_by_id(new_order.id))
    print("\n")

    print(f"Product after rated ({product.id}):")
    pprint(product_repo.find_by_id(product.id))

    # Test: List all orders
    print("📋 List of All Orders:")
    pprint(order_repo.list_all())
    print("\n")

    # Test: Delete product
    product_repo.delete(product.id)
    print(f"❌ Product Deleted ({product.id}):")
    pprint(product_repo.list_all())
    print("\n")

def test_sqlite_repositories():
    print("🗄️ Testing SQLite Repositories")
    # Ensure tables are created
    from sqlalchemy.exc import OperationalError
    
    # Recreate all tables
    # db.drop_all_tables()
    # db.create_all_tables()
    
    # Initialize SQLite repositories
    session = db.get_session()

    # Initialize SQLite repositories
    product_repo = SQLiteProductRepository()
    order_repo = SQLiteOrderRepository()
    inventory_repo = SQLiteInventoryRepository()

    print("✅ Initial Product List:")
    product_list = product_repo.list_all()
    order_product_id= product_list[0].id
    # pprint(product_list)
    print("\n")

    # Test: Create new product
    new_product = Product(name="Wireless Gaming Mouse", price=120)
    print("➕ Product Created:")
    created_product = product_repo.create(new_product)
    pprint(created_product)
    print("\n")

    # Test: Update product
    created_product.average_rating = 4.4
    created_product.name = f"{created_product.name} - Updated"
    product_repo.update(created_product)
    print("✏️ Product Updated (rating):")
    updated_product = product_repo.find_by_id(created_product.id)
    pprint(updated_product)
    print("\n")

    # Test: Add inventory
    inventory_repo.add(Inventory(product_id=order_product_id, quantity=10))
    print("➕ Inventory after adding 10 units:")
    pprint(inventory_repo.list_all())
    print("\n")

    # Test: Remove inventory
    inventory_repo.remove(product_id=order_product_id, quantity=3)
    print("➖ Inventory after removing 3 units:")
    pprint(inventory_repo.list_all())
    print("\n")

    # Test: Create order
    items = [OrderItem(product_id=order_product_id, quantity=2)]
    new_order = Order(
        customer_document="sqlite_test_user", 
        customer_name="SQLite Test Customer", 
        items=items, 
    )
    saved_order =order_repo.create(new_order)
    print("📦 Order Created:")
    pprint(saved_order)
    print("\n")

    # Test: Rate order
    print(f"Product before rated ({order_product_id}):")
    pprint(product_repo.find_by_id(order_product_id))

    order_repo.rate(saved_order.id, 1.1)
    print("🌟 Order Rated:")
    rated_order = order_repo.find_by_id(saved_order.id)
    pprint(rated_order)
    print("\n")

    print(f"Product after rated ({order_product_id}):")
    pprint(product_repo.find_by_id(order_product_id))

    # Test: List all orders
    print("📋 List of All Orders:")
    pprint(order_repo.list_all())
    print("\n")

    # Test: Delete product
    product_repo.delete(created_product.id)
    print("❌ Product Deleted:")
    # pprint(product_repo.list_all())
    print("\n")

def run_all_tests():
    print("🚀 Running Repository Tests\n")
    test_memory_repositories()
    # test_sqlite_repositories()

if __name__ == "__main__":
    run_all_tests()