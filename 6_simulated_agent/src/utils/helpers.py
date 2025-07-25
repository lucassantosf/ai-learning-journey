from src.models.product import Product

def get_products():
    return {
        "p001": Product(id="p001", name="Gaming Notebook X15", price=2999, quantity=10, average_rating=4.7),
        "p002": Product(id="p002", name="Smartphone Z Pro", price=2500, quantity=25, average_rating=4.3),
        "p003": Product(id="p003", name="Bluetooth Earbuds Airdots", price=149, quantity=40, average_rating=4.5),
        "p004": Product(id="p004", name="Smart TV 55\" 4K", price=3999, quantity=5, average_rating=4.8),
        "p005": Product(id="p005", name="RGB Mechanical Keyboard", price=120, quantity=15, average_rating=4.2),
        "p006": Product(id="p006", name="Gaming Mouse 7200DPI", price=30, quantity=30, average_rating=4.6),
        "p007": Product(id="p007", name="27\" Full HD Monitor", price=300, quantity=12, average_rating=4.4),
        "p008": Product(id="p008", name="Pro Ergonomic Chair", price=400, quantity=8, average_rating=4.9),
        "p009": Product(id="p009", name="USB-C 6-in-1 Hub", price=25, quantity=22, average_rating=4.1),
        "p010": Product(id="p010", name="Full HD 1080p Webcam", price=75, quantity=18, average_rating=4.0),
    }
