from dataclasses import dataclass, field
import uuid

@dataclass
class Product:
    name: str
    price: float
    average_rating: float = 0.0
    image_url: str = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
