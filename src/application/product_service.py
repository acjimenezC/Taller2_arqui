"""Application service for product use cases.

Orcuesta la lógica de negocio relacionada con productos:
- Obtener todos los productos
- Buscar un producto por ID
- Filtrar productos por marca y/o categoría
- Crear, actualizar y eliminar productos
Actúa como intermediario entre la API y el repositorio de datos.
"""

from __future__ import annotations

from src.domain.entities import Product
from src.domain.exceptions import ProductNotFoundError
from src.domain.repositories import IProductRepository


class ProductService:
    """Handles product-related application use cases."""

    def __init__(self, product_repository: IProductRepository) -> None:
        """Inicializa el servicio de productos.

        Recibe e inyecta la dependencia del repositorio de productos.

        Args:
            product_repository: Implementación del repositorio IProductRepository.
        """
        self._product_repository = product_repository

    def get_all_products(self) -> list[Product]:
        """Obtiene todos los productos del catálogo.

        Recupera la lista completa de productos disponibles en el repositorio.

        Returns:
            list[Product]: Lista de todos los productos del catálogo.
        """
        return self._product_repository.get_all()

    def get_product_by_id(self, product_id: int) -> Product:
        """Obtiene un producto específico por su ID.

        Busca en el repositorio un producto con el ID especificado.
        Lanza excepción si no existe.

        Args:
            product_id: ID único del producto a buscar.

        Returns:
            Product: Entidad del producto solicitado.

        Raises:
            ProductNotFoundError: Si ningún producto tiene ese ID.
        """
        product = self._product_repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product with id {product_id} was not found")
        return product

    def filter_products(self, brand: str | None = None, category: str | None = None) -> list[Product]:
        """Filtra productos por marca y/o categoría.

        Realiza búsquedas case-insensitive parciales en los campos
        de marca y categoría. Devuelve solo los productos que coinciden
        con TODOS los filtros especificados (AND lógico).

        Args:
            brand: Filtro opcional por marca (búsqueda parcial).
            category: Filtro opcional por categoría (búsqueda parcial).

        Returns:
            list[Product]: Lista de productos que coinciden con los filtros.

        Example:
            >>> service.filter_products(brand="Nike", category="Running")
            [Product(...), Product(...)]
        """
        return self._product_repository.filter(brand=brand, category=category)

    def create_product(self, product: Product) -> Product:
        """Crea un nuevo producto en el catálogo.

        Valida los datos del producto mediante la entidad de dominio
        antes de persistir en la base de datos.

        Args:
            product: Entidad Product con datos del nuevo producto.

        Returns:
            Product: Producto persistido en BD con ID asignado.

        Raises:
            InvalidProductDataError: Si los datos del producto son inválidos.
        """
        return self._product_repository.create(product)

    def update_product(self, product_id: int, product: Product) -> Product:
        """Actualiza los datos de un producto existente.

        Busca el producto por ID, valida los nuevos datos
        y persiste los cambios en la BD.

        Args:
            product_id: ID del producto a actualizar.
            product: Entidad Product con los nuevos datos.

        Returns:
            Product: Producto actualizado persistido en BD.

        Raises:
            ProductNotFoundError: Si el producto no existe.
            InvalidProductDataError: Si los nuevos datos son inválidos.
        """
        existing = self._product_repository.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(f"Product with id {product_id} was not found")

        product.id = product_id
        return self._product_repository.update(product)

    def delete_product(self, product_id: int) -> None:
        """Elimina un producto del catálogo.

        Busca y elimina permanentemente un producto del repositorio.
        Si el producto no existe, lanza excepción.

        Args:
            product_id: ID del producto a eliminar.

        Raises:
            ProductNotFoundError: Si el producto con ese ID no existe.
        """
        existing = self._product_repository.get_by_id(product_id)
        if existing is None:
            raise ProductNotFoundError(f"Product with id {product_id} was not found")
        self._product_repository.delete(product_id)

    def sell_product(self, product_id: int, quantity: int = 1) -> Product:
        """Apply a sale operation and reduce stock.

        Reduce el inventario de un producto cuando se realiza una venta.
        Valida que haya stock suficiente antes de proceder.

        Args:
            product_id: ID del producto a vender.
            quantity: Cantidad de unidades a vender (por defecto 1).

        Returns:
            Product: Producto actualizado con stock reducido.

        Raises:
            ProductNotFoundError: Si el producto no existe.
            InvalidProductDataError: Si no hay stock suficiente.

        Raises:
            ProductNotFoundError: If product does not exist.
        """
        product = self.get_product_by_id(product_id)
        product.decrease_stock(quantity)
        return self._product_repository.update(product)
