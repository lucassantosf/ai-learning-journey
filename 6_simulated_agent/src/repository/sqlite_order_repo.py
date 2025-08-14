from typing import List, Optional
from sqlalchemy.orm.exc import NoResultFound
from src.repository.interfaces.order_repository import OrderRepository
from src.models.order import Order, OrderItem
from src.repository.sqlite_base import db
from src.repository.sqlite_models import OrderModel, OrderItemModel, ProductModel
from datetime import datetime

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
                user_id=model.user_id,
                customer_name=model.customer_name,
                creation_date=model.creation_date,
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
                user_id=model.user_id,
                customer_name=model.customer_name,
                creation_date=model.creation_date,
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
        # Generate a unique ID if not provided
        if not order.id:
            order.id = f"order_{self.session.query(OrderModel).count() + 1:03d}"

        # Calculate total price
        total_price = 0
        
        # Create order model
        order_model = OrderModel(
            id=order.id,
            user_id=order.user_id,
            customer_name=order.customer_name,
            creation_date=order.creation_date or datetime.now(),
            rating=order.rating
        )
        
        self.session.add(order_model)

        # Create order items
        for item in order.items:
            # Find product to get its price
            product = self.session.query(ProductModel).filter_by(id=item.product_id).one()
            
            order_item_model = OrderItemModel(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            
            self.session.add(order_item_model)

        self.session.commit()

    def rate(self, order_id: str, rating: int) -> None:
        """
        Rate an order
        
        :param order_id: ID of the order to rate
        :param rating: Rating value
        """
        try:
            order_model = self.session.query(OrderModel).filter_by(id=order_id).one()
            order_model.rating = rating
            self.session.commit()
        except NoResultFound:
            pass  # Silently ignore if order not found
