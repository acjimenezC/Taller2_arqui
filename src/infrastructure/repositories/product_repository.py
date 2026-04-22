"""SQL repository implementation for products."""

from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel


class ProductRepository(IProductRepository):
    """SQLAlchemy implementation of product repository."""

    def __init__(self, db: Session) -> None:
        """Store database dependency.

        Args:
            db: SQLAlchemy session.
        """
        self._db = db

    def get_all(self) -> list[Product]:
        """Return all products."""
        result = self._db.execute(select(ProductModel).order_by(ProductModel.id.asc()))
        return [self._to_entity(model) for model in result.scalars().all()]

    def get_by_id(self, product_id: int) -> Product | None:
        """Return one product by id."""
        result = self._db.execute(select(ProductModel).where(ProductModel.id == product_id)).scalar_one_or_none()
        return self._to_entity(result) if result else None

    def filter(self, brand: str | None = None, category: str | None = None) -> list[Product]:
        """Filter products by brand and/or category."""
        statement: Select[tuple[ProductModel]] = select(ProductModel)
        if brand:
            statement = statement.where(ProductModel.brand.ilike(f"%{brand}%"))
        if category:
            statement = statement.where(ProductModel.category.ilike(f"%{category}%"))
        statement = statement.order_by(ProductModel.id.asc())

        result = self._db.execute(statement).scalars().all()
        return [self._to_entity(model) for model in result]

    def create(self, product: Product) -> Product:
        """Create and return one product."""
        model = ProductModel(
            name=product.name,
            brand=product.brand,
            category=product.category,
            size=product.size,
            color=product.color,
            price=product.price,
            stock=product.stock,
            description=product.description,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def update(self, product: Product) -> Product:
        """Update one product and return persisted entity."""
        model = self._db.execute(select(ProductModel).where(ProductModel.id == product.id)).scalar_one()
        model.name = product.name
        model.brand = product.brand
        model.category = product.category
        model.size = product.size
        model.color = product.color
        model.price = product.price
        model.stock = product.stock
        model.description = product.description
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    def delete(self, product_id: int) -> None:
        """Delete one product by id."""
        model = self._db.execute(select(ProductModel).where(ProductModel.id == product_id)).scalar_one_or_none()
        if model is None:
            return
        self._db.delete(model)
        self._db.commit()

    @staticmethod
    def _to_entity(model: ProductModel) -> Product:
        """Map ORM model to domain entity.

        Args:
            model: ORM model.

        Returns:
            Product: Domain entity.
        """
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )
