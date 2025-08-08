from datetime import datetime
from pprint import pprint
from src.repository.product_mem_repo import ProductMemRepository
from src.repository.order_mem_repo import OrderMemRepository
from src.repository.inventory_mem_repo import InventoryMemRepository
from src.models.product import Product
from src.models.order import Order, OrderItem
from src.models.inventory import Inventory

def test_repositories():
    # Initialize repositories
    product_repo = ProductMemRepository()
    order_repo = OrderMemRepository()
    inventory_repo = InventoryMemRepository()

    print("✅ Available Products:")
    pprint(product_repo.list_all())
    print("\n")

    # Test: Create new product
    new_product = Product(name="RGB Gaming Headset", price=150)
    product_repo.create(new_product)
    print("➕ Product Created:")
    pprint(product_repo.find_by_id("p011"))
    print("\n")

    # Test: Update product
    product_to_update = product_repo.find_by_id("p011")
    product_to_update.average_rating = 4.7
    product_repo.update(product_to_update)
    print("✏️ Product Updated (rating):")
    pprint(product_repo.find_by_id("p011"))
    print("\n")

    # Test: Add inventory
    inventory_repo.add(Inventory(product_id="p011", quantity=5))
    print("➕ Inventory after adding 5 units:")
    pprint(inventory_repo.list_all())
    print("\n")

    # Test: Remove inventory
    inventory_repo.remove(product_id="p011", quantity=3)
    print("➖ Inventory after removing 3 units:")
    pprint(inventory_repo.list_all())
    print("\n")

    # Test: Create order
    items = [OrderItem(product_id="p001", quantity=1), OrderItem(product_id="p002", quantity=2)]
    new_order = Order(
        id="order_001", 
        user_id="test_user", 
        customer_name="Test Customer", 
        items=items, 
        creation_date=datetime.now()
    )
    order_repo.create(new_order)
    print("📦 Order Created:")
    pprint(order_repo.find_by_id("order_001"))
    print("\n")

    # Test: Rate order
    order_repo.rate("order_001", 4.8)
    print("🌟 Order Rated:")
    pprint(order_repo.find_by_id("order_001"))
    print("\n")

    # Test: List all orders
    print("📋 List of All Orders:")
    pprint(order_repo.list_all())
    print("\n")

    # Test: Delete product
    product_repo.delete("p011")
    print("❌ Product Deleted (p011):")
    pprint(product_repo.list_all())
    print("\n")

if __name__ == "__main__":
    test_repositories()
