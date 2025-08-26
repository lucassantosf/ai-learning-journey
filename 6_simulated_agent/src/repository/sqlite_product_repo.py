from typing import List, Optional
from sqlalchemy.orm.exc import NoResultFound
from src.repository.interfaces.product_repository import ProductRepository
from src.models.product import Product
from src.repository.sqlite_base import db
from src.repository.sqlite_models import ProductModel
import uuid
from sqlalchemy.orm import joinedload

class SQLiteProductRepository(ProductRepository):
    def __init__(self):
        self.session = db.get_session()

    def list_all(self) -> List[Product]:
        """
        List all products from the database
        
        :return: List of Product objects
        """
        product_models = (
            self.session.query(ProductModel)
            .options(joinedload(ProductModel.inventory))  # carrega estoque junto
            .all()
        )

        products = []

        for model in product_models:
            # cria o Product normal
            product = Product(
                id=model.id,
                name=model.name,
                price=model.price,
                average_rating=model.average_rating,
                image_url=model.image_url,
            )

            # adiciona quantity dinamicamente
            product.quantity = model.inventory.quantity if model.inventory else 0

            products.append(product)

        return products

    def find_by_id(self, product_id: str) -> Optional[Product]:
        """
        Find a product by its ID
        
        :param product_id: Product ID to search
        :return: Product object or None
        """
        try:
            model = (       
                self.session.query(ProductModel)
                .options(joinedload(ProductModel.inventory))
                .filter_by(id=product_id)
                .one_or_none()
            )

            if not model:
                return None
            
            product = Product(
                id=model.id,
                name=model.name,
                price=model.price,
                average_rating=model.average_rating,
                image_url=model.image_url
            )
        
            # adiciona quantity dinamicamente
            product.quantity = model.inventory.quantity if model.inventory else 0

            return product

        except NoResultFound:
            return None

    def find_by_name(self, product_name: str) -> Optional[Product]:
        """
        Find the first product that matches the given name.
        Quantity comes from the related Inventory table.
        """
        try:
            model = (
                self.session.query(ProductModel)
                .filter(ProductModel.name.ilike(f"%{product_name}%"))
                .first()
            )

            if model:
                # pega a quantidade do relacionamento inventory
                quantity = model.inventory.quantity if model.inventory else 0  

                return Product(
                    id=model.id,
                    name=model.name,
                    price=model.price,
                    quantity=quantity,
                    average_rating=model.average_rating,
                    image_url=model.image_url
                )
            return None
        except Exception:
            return None

    def create(self, product: Product) -> Product:
        """
        Create a new product in the database
        
        :param product: Product object to create
        """
        product_model = ProductModel(
            id=product.id,
            name=product.name,
            price=product.price,
            average_rating=product.average_rating or 0.0,
            image_url=product.image_url
        )
        
        self.session.add(product_model)
        self.session.commit()
        self.session.refresh(product_model)  # ⚡ garante que os dados do banco estão atualizados

        # Constrói e retorna um Product limpo com os dados do banco
        return Product(
            id=product_model.id,
            name=product_model.name,
            price=product_model.price,
            average_rating=0,
            image_url=product_model.image_url,
        )

    def update(self, product: Product) -> None:
        """
        Update an existing product in the database
        
        :param product: Product object to update
        """
        try:
            product_model = self.session.query(ProductModel).filter_by(id=product.id).one()
            
            product_model.name = product.name
            product_model.price = product.price
            product_model.average_rating = product.average_rating
            product_model.image_url = product.image_url
            
            self.session.commit()
        except NoResultFound:
            # If product not found, create a new one
            self.create(product)

    def delete(self, product_id: str) -> None:
        """
        Delete a product from the database
        
        :param product_id: ID of the product to delete
        """
        try:
            product_model = self.session.query(ProductModel).filter_by(id=product_id).one()
            self.session.delete(product_model)
            self.session.commit()
        except NoResultFound:
            return None