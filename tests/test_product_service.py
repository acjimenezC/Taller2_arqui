"""Tests for product application service."""

from __future__ import annotations

from src.application.product_service import ProductService
from src.domain.entities import Product
from src.domain.exceptions import ProductNotFoundError
from src.domain.repositories import IProductRepository


class InMemoryProductRepository(IProductRepository):
    """In-memory repository for product service tests."""

    def __init__(self) -> None:
        self._items: dict[int, Product] = {}
        self._next_id = 1

    def get_all(self) -> list[Product]:
        return list(self._items.values())

    def get_by_id(self, product_id: int) -> Product | None:
        return self._items.get(product_id)

    def filter(self, brand: str | None = None, category: str | None = None) -> list[Product]:
        items = self.get_all()
        if brand:
            items = [p for p in items if brand.lower() in p.brand.lower()]
        if category:
            items = [p for p in items if category.lower() in p.category.lower()]
        return items

    def create(self, product: Product) -> Product:
        product.id = self._next_id
        self._items[self._next_id] = product
        self._next_id += 1
        return product

    def update(self, product: Product) -> Product:
        self._items[product.id or 0] = product
        return product

    def delete(self, product_id: int) -> None:
        self._items.pop(product_id, None)


def _sample_product() -> Product:
    return Product(
        id=None,
        name="Court Vision",
        brand="Nike",
        category="Casual",
        size=41,
        color="Blanco",
        price=85,
        stock=10,
        description="Inspirada en basket",
    )


def test_create_and_get_product() -> None:
    repo = InMemoryProductRepository()
    service = ProductService(repo)

    created = service.create_product(_sample_product())

    assert created.id == 1
    assert service.get_product_by_id(1).name == "Court Vision"


def test_get_product_not_found_raises_error() -> None:
    repo = InMemoryProductRepository()
    service = ProductService(repo)

    try:
        service.get_product_by_id(999)
        assert False
    except ProductNotFoundError:
        assert True


def test_sell_product_reduces_stock() -> None:
    repo = InMemoryProductRepository()
    service = ProductService(repo)
    created = service.create_product(_sample_product())

    updated = service.sell_product(created.id or 0, quantity=2)

    assert updated.stock == 8
