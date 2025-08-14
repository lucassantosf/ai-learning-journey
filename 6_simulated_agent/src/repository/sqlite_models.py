from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.repository.sqlite_base import Base
from datetime import datetime

class ProductModel(Base):
    __tablename__ = 'products'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.now)

class OrderModel(Base):
    __tablename__ = 'orders'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)
    creation_date = Column(DateTime, default=datetime.now)
    rating = Column(Float)

    # Relationship to OrderItemModel
    items = relationship('OrderItemModel', back_populates='order', cascade='all, delete-orphan')

class OrderItemModel(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, ForeignKey('orders.id'))
    product_id = Column(String, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)

    # Relationships
    order = relationship('OrderModel', back_populates='items')
    product = relationship('ProductModel')

class InventoryModel(Base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, ForeignKey('products.id'), unique=True)
    quantity = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationship to ProductModel
    product = relationship('ProductModel')
