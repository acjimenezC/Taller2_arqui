"""Tests for domain entities and validations."""

from __future__ import annotations

import pytest

from src.domain.entities import Product
from src.domain.exceptions import InvalidProductDataError


def test_product_price_must_be_greater_than_zero() -> None:
    """Should reject product with non-positive price."""
    with pytest.raises(InvalidProductDataError):
        Product(
            id=None,
            name="Pegasus",
            brand="Nike",
            category="Running",
            size=41,
            color="Negro",
            price=0,
            stock=5,
            description="Zapato running",
        )


def test_product_stock_cannot_be_negative() -> None:
    """Should reject product with negative stock."""
    with pytest.raises(InvalidProductDataError):
        Product(
            id=None,
            name="RS-X",
            brand="Puma",
            category="Casual",
            size=40,
            color="Gris",
            price=95,
            stock=-1,
            description="Zapato casual",
        )


def test_decrease_stock_prevents_sale_without_stock() -> None:
    """Should prevent selling more than available stock."""
    product = Product(
        id=1,
        name="Ultraboost",
        brand="Adidas",
        category="Running",
        size=42,
        color="Blanco",
        price=180,
        stock=1,
        description="Running premium",
    )

    with pytest.raises(InvalidProductDataError):
        product.decrease_stock(quantity=2)
