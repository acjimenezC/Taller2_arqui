"""Application service for product use cases."""

from __future__ import annotations

from src.domain.entities import Product
from src.domain.exceptions import ProductNotFoundError
from src.domain.repositories import IProductRepository


class ProductService:
    """Handles product-related application use cases."""

    def __init__(self, product_repository: IProductRepository) -> None:
        """Initialize service dependencies.

        Args:
            product_repository: Repository implementation for products.
        """
        self._product_repository = product_repository

    def get_all_products(self) -> list[Product]:
        """Get all products from repository.

        Returns:
            list[Product]: All products.
        """
        return self._product_repository.get_all()

    def get_product_by_id(self, product_id: int) -> Product:
        """Get one product by id.

        Args:
            product_id: Product id.

        Returns:
            Product: Existing product.

        Raises:
            ProductNotFoundError: If product does not exist.
        """
        product = self._product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product with id {product_id} was not found")
        return product

    def filter_products(self, brand: str | None = None, category: str | None = None) -> list[Product]:
        """Filter products by brand and/or category.

        Args:
            brand: Optional brand filter.
            category: Optional category filter.

        Returns:
            list[Product]: Matching products.
        """
        return self._product_repository.filter(brand=brand, category=category)

    def create_product(self, product: Product) -> Product:
        """Create a new product.

        Args:
            product: Product entity.

        Returns:
            Product: Persisted product.
        """
        return self._product_repository.create(product)

    def update_product(self, product_id: int, product: Product) -> Product:
        """Update an existing product.

        Args:
            product_id: Product id to update.
            product: New entity data.

        Returns:
            Product: Updated product.

        Raises:
            ProductNotFoundError: If product does not exist.
        """
        existing = self._product_repository.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(f"Product with id {product_id} was not found")

        product.id = product_id
        return self._product_repository.update(product)

    def delete_product(self, product_id: int) -> None:
        """Delete product by id.

        Args:
            product_id: Product id.

        Raises:
            ProductNotFoundError: If product does not exist.
        """
        existing = self._product_repository.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(f"Product with id {product_id} was not found")
        self._product_repository.delete(product_id)

    def sell_product(self, product_id: int, quantity: int = 1) -> Product:
        """Apply a sale operation and reduce stock.

        Args:
            product_id: Product id.
            quantity: Units sold.

        Returns:
            Product: Updated product with reduced stock.

        Raises:
            ProductNotFoundError: If product does not exist.
        """
        product = self.get_product_by_id(product_id)
        product.decrease_stock(quantity)
        return self._product_repository.update(product)
