import uuid
from src.models.product import Product

def get_products():
    products = [
        Product(id=str(uuid.uuid4()), name="Gaming Notebook X15", price=2999, quantity=10, average_rating=4.7, image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Smartphone Z Pro", price=2500, quantity=25, average_rating=4.3, image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Bluetooth Earbuds Airdots", price=149, quantity=40, average_rating=4.5, image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Smart TV 55\" 4K", price=3999, quantity=5, average_rating=4.8, image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="RGB Mechanical Keyboard", price=120, quantity=15, average_rating=4.2, image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Gaming Mouse 7200DPI", price=30, quantity=30, average_rating=4.6, image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="27\" Full HD Monitor", price=300, quantity=12, average_rating=4.4, image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Pro Ergonomic Chair", price=400, quantity=8, average_rating=4.9, image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="USB-C 6-in-1 Hub", price=25, quantity=22, average_rating=4.1, image_url="https://picsum.photos/300/200"),
        Product(id=str(uuid.uuid4()), name="Full HD 1080p Webcam", price=75, quantity=18, average_rating=4.0, image_url="https://picsum.photos/300/200"),
    ]

    return {product.id: product for product in products}
