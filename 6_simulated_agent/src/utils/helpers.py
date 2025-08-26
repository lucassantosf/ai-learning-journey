import uuid
from src.models.product import Product
import random

def get_products():
    products = [
        Product(id=str(uuid.uuid4()), name="Gaming Notebook X15", price=2999, average_rating=round(random.uniform(3.0, 5.0), 2), image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Smartphone Z Pro", price=2500, average_rating=round(random.uniform(3.0, 5.0), 2), image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Bluetooth Earbuds Airdots", price=149, average_rating=round(random.uniform(3.0, 5.0), 2), image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Smart TV 55\" 4K", price=3999, average_rating=round(random.uniform(3.0, 5.0), 2), image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="RGB Mechanical Keyboard", price=120, average_rating=round(random.uniform(3.0, 5.0), 2), image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Gaming Mouse 7200DPI", price=30, average_rating=round(random.uniform(3.0, 5.0), 2), image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="27\" Full HD Monitor", price=300, average_rating=round(random.uniform(3.0, 5.0), 2), image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Pro Ergonomic Chair", price=400, average_rating=round(random.uniform(3.0, 5.0), 2), image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="USB-C 6-in-1 Hub", price=25, average_rating=round(random.uniform(3.0, 5.0), 2), image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Full HD 1080p Webcam", price=75, average_rating=round(random.uniform(3.0, 5.0), 2), image_url="https://picsum.photos/300/200"),
    ]

    return {product.id: product for product in products}
