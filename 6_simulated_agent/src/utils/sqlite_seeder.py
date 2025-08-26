from src.models.product import Product
from src.repository.sqlite_base import db
from src.repository.sqlite_product_repo import SQLiteProductRepository
from src.repository.sqlite_inventory_repo import SQLiteInventoryRepository
from src.models.inventory import Inventory
from src.utils.helpers import get_products
import random

def seed_sqlite_products():
    """
    Seed SQLite database with initial products from get_products()
    
    This function will:
    1. Drop existing tables
    2. Recreate tables
    3. Add products to SQLite database
    4. Add corresponding inventory
    """
    # Initialize repositories
    product_repo = SQLiteProductRepository()
    inventory_repo = SQLiteInventoryRepository()

    # Drop and recreate all tables
    db.drop_all_tables()
    db.create_all_tables()

    # Get initial products
    initial_products = get_products()

    # Add products and their inventory
    for product_id, product in initial_products.items():
        # Create product in SQLite
        product_repo.create(product)

        # Add inventory for the product
        inventory = Inventory(
            product_id=product_id,
            quantity=random.randint(5, 20),  # Random initial stock between 5 and 20
        )
        inventory_repo.add(inventory)

    print("🌱 Initial products seeded in SQLite successfully!")
    return initial_products

# If this script is run directly, seed the products
if __name__ == "__main__":
    seed_sqlite_products()