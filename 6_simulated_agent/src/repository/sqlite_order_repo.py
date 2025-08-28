from typing import List, Optional
from sqlalchemy.orm.exc import NoResultFound
from src.repository.interfaces.order_repository import OrderRepository
from src.models.order import Order, OrderItem
from src.repository.sqlite_base import db
from src.repository.sqlite_models import OrderModel, OrderItemModel, ProductModel, InventoryModel

class SQLiteOrderRepository(OrderRepository):
    def __init__(self):
        self.session = db.get_session()

    def list_all(self) -> List[Order]:
        """
        List all orders from the database
        
        :return: List of Order objects
        """
        order_models = self.session.query(OrderModel).all()
        return [
            Order(
                id=model.id,
                customer_document=model.customer_document,
                customer_name=model.customer_name,
                created_at=model.created_at,
                rating=model.rating,
                items=[
                    OrderItem(
                        product_id=item.product_id, 
                        quantity=item.quantity
                    ) for item in model.items
                ]
            ) for model in order_models
        ]

    def find_by_id(self, order_id: str) -> Optional[Order]:
        """
        Find an order by its ID
        
        :param order_id: Order ID to search
        :return: Order object or None
        """
        try:
            model = self.session.query(OrderModel).filter_by(id=order_id).one()
            return Order(
                id=model.id,
                customer_document=model.customer_document,
                customer_name=model.customer_name,
                created_at=model.created_at,
                rating=model.rating,
                items=[
                    OrderItem(
                        product_id=item.product_id, 
                        quantity=item.quantity
                    ) for item in model.items
                ]
            )
        except NoResultFound:
            return None

    def create(self, order: Order) -> None:
        """
        Create a new order in the database
        
        :param order: Order object to create
        """
        # Create order model
        order_model = OrderModel(
            customer_document=order.customer_document,
            customer_name=order.customer_name,
        )
        self.session.add(order_model)
        self.session.flush()  # força preencher o order_model.id antes do commit

        # Create order items
        for item in order.items:

            # validate inventory
            inventory_model = self.session.query(InventoryModel).filter_by(product_id=item.product_id).one()
            
            if inventory_model.quantity < item.quantity:
                raise ValueError(f"Insufficient inventory for product {item.product_id}")
            
            # criar referencia do item
            order_item_model = OrderItemModel(
                order_id=order_model.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            self.session.add(order_item_model)

            # Atualiza o inventário
            inventory_model.quantity -= item.quantity
            self.session.commit()

        self.session.commit()

        # Atualiza o dataclass com o id real do banco
        order.id = order_model.id
        for i, item in enumerate(order.items):
            order.items[i].id = item.id  # idem pros items, se precisar
        
        return order

    def rate(self, order_id: str, rating: int) -> None:
        """
        Rate an order and update the average rating of its products
        """
        try:
            order_model = self.session.query(OrderModel).filter_by(id=order_id).one()
            order_model.rating = rating

            # Atualiza os produtos do pedido
            for item in order_model.items:
                product = self.session.query(ProductModel).filter_by(id=item.product_id).one_or_none()
                if product:
                    if product.average_rating is None:
                        product.average_rating = rating
                    else:
                        product.average_rating = (product.average_rating + rating) / 2

            self.session.commit()

        except NoResultFound:
            pass  # Silently ignore if order not found
