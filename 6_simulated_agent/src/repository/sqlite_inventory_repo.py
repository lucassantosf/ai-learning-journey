from typing import List, Optional
from sqlalchemy.orm.exc import NoResultFound
from src.repository.interfaces.inventory_repository import InventoryRepository
from src.models.inventory import Inventory
from src.repository.sqlite_base import db
from src.repository.sqlite_models import InventoryModel

class SQLiteInventoryRepository(InventoryRepository):
    def __init__(self):
        self.session = db.get_session()

    def list_all(self) -> List[Inventory]:
        """
        List all inventory items from the database
        
        :return: List of Inventory objects
        """
        inventory_models = self.session.query(InventoryModel).all()
        return [
            Inventory(
                product_id=model.product_id,
                quantity=model.quantity,
                product_name=model.product.name if model.product else None
            ) for model in inventory_models
        ]

    def add(self, inventory: Inventory) -> None:
        """
        Add or update inventory for a product
        
        :param inventory: Inventory object to add/update
        """
        try:
            # Check if inventory for this product already exists
            inventory_model = self.session.query(InventoryModel).filter_by(product_id=inventory.product_id).first()
            
            if inventory_model:
                # Update existing inventory
                inventory_model.quantity += inventory.quantity
            else:
                # Create new inventory entry
                inventory_model = InventoryModel(
                    product_id=inventory.product_id,
                    quantity=inventory.quantity
                )
                self.session.add(inventory_model)
            
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def remove(self, product_id: str, quantity: int) -> None:
        """
        Remove quantity from product inventory
        
        :param product_id: ID of the product
        :param quantity: Quantity to remove
        """
        try:
            inventory_model = self.session.query(InventoryModel).filter_by(product_id=product_id).one()
            
            if inventory_model.quantity < quantity:
                raise ValueError(f"Insufficient inventory for product {product_id}")
            
            inventory_model.quantity -= quantity
            self.session.commit()
        except NoResultFound:
            raise ValueError(f"No inventory found for product {product_id}")
