"""SQL repository implementation for products.

Implementa la interfaz IProductRepository usando SQLAlchemy.
Realiza operaciones CRUD (Create, Read, Update, Delete) en la tabla de productos.
Convierte entre modelos SQLAlchemy y entidades del dominio.
Maneja consultas SQL de forma segura contra inyección.
"""

from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel


class ProductRepository(IProductRepository):
    """SQLAlchemy implementation of product repository."""

    def __init__(self, db: Session) -> None:
        """Inicializa el repositorio de productos.

        Guarda la sesión de SQLAlchemy para todas las operaciones CRUD.

        Args:
            db: Sesión SQLAlchemy activa.
        """
        self._db = db

    def get_all(self) -> list[Product]:
        """Obtiene todos los productos de la base de datos.

        Recupera la lista completa de productos ordenados por ID
        en orden ascendente.

        Returns:
            list[Product]: Lista de todas las entidades Product.
        """
        result = self._db.execute(select(ProductModel).order_by(ProductModel.id.asc()))
        return [self._to_entity(model) for model in result.scalars().all()]

    def get_by_id(self, product_id: int) -> Product | None:
        """Obtiene un producto por su ID.

        Busca en la BD un producto con el ID especificado.
        Retorna None si no existe.

        Args:
            product_id: ID único del producto.

        Returns:
            Product: Producto encontrado, o None si no existe.
        """
        result = self._db.execute(select(ProductModel).where(ProductModel.id == product_id)).scalar_one_or_none()
        return self._to_entity(result) if result else None

    def filter(self, brand: str | None = None, category: str | None = None) -> list[Product]:
        """Filtra productos por marca y categoría.

        Realiza búsquedas case-insensitive parciales usando ILIKE.
        Retorna solo los productos que coincidan con TODOS los filtros.

        Args:
            brand: Filtro opcional por marca (búsqueda parcial).
            category: Filtro opcional por categoría (búsqueda parcial).

        Returns:
            list[Product]: Productos que coinciden con los filtros.
        """
        statement: Select[tuple[ProductModel]] = select(ProductModel)
        if brand:
            statement = statement.where(ProductModel.brand.ilike(f"%{brand}%"))
        if category:
            statement = statement.where(ProductModel.category.ilike(f"%{category}%"))
        statement = statement.order_by(ProductModel.id.asc())

        result = self._db.execute(statement).scalars().all()
        return [self._to_entity(model) for model in result]

    def create(self, product: Product) -> Product:
        """Crea un nuevo producto en la BD.

        Convierte la entidad de dominio a modelo ORM,
        persiste en BD y retorna la entidad con ID asignado.

        Args:
            product: Entidad Product a crear.

        Returns:
            Product: Producto con ID asignado por la BD.
        """
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
        """Actualiza un producto existente.

        Busca el modelo ORM por ID, actualiza todos sus campos
        desde la entidad de dominio y persiste en BD.

        Args:
            product: Entidad Product con datos actualizados.

        Returns:
            Product: Producto actualizado.

        Raises:
            sqlalchemy.exc.NoResultFound: Si el producto no existe.
        """
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
        """Elimina un producto de la BD.

        Busca y elimina el producto con el ID especificado.
        No lanza error si el producto no existe (idempotente).

        Args:
            product_id: ID del producto a eliminar.
        """
        model = self._db.execute(select(ProductModel).where(ProductModel.id == product_id)).scalar_one_or_none()
        if model is None:
            return
        self._db.delete(model)
        self._db.commit()

    @staticmethod
    def _to_entity(model: ProductModel) -> Product:
        """Convierte un modelo ORM a entidad de dominio.

        Mapea los campos del modelo SQLAlchemy al objeto Product
        de dominio para mantener la separación de capas.

        Args:
            model: Modelo ORM ProductModel de SQLAlchemy.

        Returns:
            Product: Entidad de dominio equivalente.
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
