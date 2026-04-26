"""Domain repository interfaces.

Define contratos (interfaces abstractas) para acceder a datos.
Actúan como puertos que pueden ser implementados por cualquier tecnología
(SQL, NoSQL, API remota, etc.) sin afectar la lógica de negocio.
Permiten el patrón de inyección de dependencias.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities import ChatMessage, Product


class IProductRepository(ABC):
    """Repository interface for product persistence."""

    @abstractmethod
    def get_all(self) -> list[Product]:
        """Return all products."""

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product | None:
        """Return one product by id."""

    @abstractmethod
    def filter(self, brand: str | None = None, category: str | None = None) -> list[Product]:
        """Filter products by optional fields."""

    @abstractmethod
    def create(self, product: Product) -> Product:
        """Create a product."""

    @abstractmethod
    def update(self, product: Product) -> Product:
        """Update a product."""

    @abstractmethod
    def delete(self, product_id: int) -> None:
        """Delete a product by id."""


class IChatRepository(ABC):
    """Repository interface for chat memory persistence."""

    @abstractmethod
    def save_message(self, session_id: str, message: ChatMessage) -> None:
        """Persist one message in chat memory."""

    @abstractmethod
    def get_recent_messages(self, session_id: str, limit: int = 6) -> list[ChatMessage]:
        """Return recent messages for one session."""

    @abstractmethod
    def get_all_messages(self, session_id: str) -> list[ChatMessage]:
        """Return full history for one session."""
