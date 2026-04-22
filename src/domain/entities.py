"""Core domain entities for the e-commerce chat backend."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from src.domain.exceptions import InvalidProductDataError


@dataclass
class Product:
    """Represents a shoe product in the catalog.

    Args:
        id: Unique identifier.
        name: Product name.
        brand: Product brand.
        category: Product category.
        size: Shoe size value.
        color: Product color.
        price: Unit price.
        stock: Current stock.
        description: Product description.
    """

    id: int | None
    name: str
    brand: str
    category: str
    size: float
    color: str
    price: float
    stock: int
    description: str

    def __post_init__(self) -> None:
        """Validate business constraints after initialization.

        Raises:
            InvalidProductDataError: If any field violates domain rules.
        """
        if not self.name.strip():
            raise InvalidProductDataError("Product name is required")
        if not self.brand.strip():
            raise InvalidProductDataError("Product brand is required")
        if not self.category.strip():
            raise InvalidProductDataError("Product category is required")
        if self.size <= 0:
            raise InvalidProductDataError("Product size must be greater than 0")
        if self.price <= 0:
            raise InvalidProductDataError("Product price must be greater than 0")
        if self.stock < 0:
            raise InvalidProductDataError("Product stock cannot be negative")

    def decrease_stock(self, quantity: int = 1) -> None:
        """Decrease stock when a sale is made.

        Args:
            quantity: Number of units to discount.

        Raises:
            InvalidProductDataError: If quantity is invalid or stock is insufficient.
        """
        if quantity <= 0:
            raise InvalidProductDataError("Sale quantity must be greater than 0")
        if self.stock < quantity:
            raise InvalidProductDataError("Cannot sell product without stock")
        self.stock -= quantity


@dataclass
class ChatMessage:
    """Represents one chat message."""

    role: str
    content: str
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate message role and content.

        Raises:
            InvalidProductDataError: If role or content is invalid.
        """
        if self.role not in {"user", "assistant"}:
            raise InvalidProductDataError("Chat message role must be 'user' or 'assistant'")
        if not self.content.strip():
            raise InvalidProductDataError("Chat message content cannot be empty")

    @classmethod
    def create(cls, role: str, content: str) -> "ChatMessage":
        """Create a chat message with UTC timestamp.

        Args:
            role: Message role.
            content: Message content.

        Returns:
            ChatMessage: New message instance.
        """
        return cls(role=role, content=content, created_at=datetime.now(timezone.utc))


@dataclass
class ChatContext:
    """Conversation context containing the most recent messages."""

    messages: list[ChatMessage]

    @classmethod
    def from_messages(cls, messages: list[ChatMessage], limit: int = 6) -> "ChatContext":
        """Build a bounded chat context.

        Args:
            messages: Full message list.
            limit: Maximum number of latest messages.

        Returns:
            ChatContext: Context with at most limit messages.
        """
        return cls(messages=messages[-limit:])
