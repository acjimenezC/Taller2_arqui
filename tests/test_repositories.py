"""Tests for SQL repositories."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage, Product
from src.infrastructure.repositories.chat_repository import ChatRepository
from src.infrastructure.repositories.product_repository import ProductRepository


def test_product_repository_create_and_filter(db_session: Session) -> None:
    """Should persist and filter products by brand."""
    repo = ProductRepository(db_session)

    repo.create(
        Product(
            id=None,
            name="Suede Classic",
            brand="Puma",
            category="Casual",
            size=39,
            color="Azul",
            price=80,
            stock=5,
            description="Iconico",
        )
    )

    products = repo.filter(brand="Puma")
    assert len(products) == 1
    assert products[0].name == "Suede Classic"


def test_chat_repository_persists_and_gets_recent_messages(db_session: Session) -> None:
    """Should store chat messages and return ordered recent records."""
    repo = ChatRepository(db_session)

    for i in range(8):
        repo.save_message(
            session_id="s1",
            message=ChatMessage(role="user" if i % 2 == 0 else "assistant", content=f"msg-{i}", created_at=datetime.now(timezone.utc)),
        )

    recent = repo.get_recent_messages("s1", limit=6)

    assert len(recent) == 6
    assert recent[0].content == "msg-2"
    assert recent[-1].content == "msg-7"
