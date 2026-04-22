"""Application service that orchestrates chat with AI."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from src.domain.entities import ChatContext, ChatMessage
from src.domain.exceptions import ChatServiceError
from src.domain.repositories import IChatRepository, IProductRepository


class ILLMProvider(ABC):
    """Port for language model providers."""

    @abstractmethod
    def generate_response(
        self,
        current_message: str,
        available_products: list,
        context: ChatContext,
    ) -> str:
        """Generate the assistant response from context and products."""


class ChatService:
    """Coordinates chat flow and persistence."""

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        llm_provider: ILLMProvider,
    ) -> None:
        """Initialize service dependencies.

        Args:
            product_repository: Product repository interface.
            chat_repository: Chat repository interface.
            llm_provider: LLM provider port.
        """
        self._product_repository = product_repository
        self._chat_repository = chat_repository
        self._llm_provider = llm_provider

    def process_message(self, session_id: str, message: str) -> tuple[str, datetime]:
        """Process one chat request end-to-end.

        Flow:
            1. Load available products.
            2. Load latest chat context.
            3. Generate response with LLM.
            4. Persist user and assistant messages.
            5. Return response.

        Args:
            session_id: Conversation session id.
            message: User message.

        Returns:
            tuple[str, datetime]: Assistant response and timestamp.

        Raises:
            ChatServiceError: If processing fails.
        """
        try:
            available_products = [p for p in self._product_repository.get_all() if p.stock > 0]
            recent_messages = self._chat_repository.get_recent_messages(session_id=session_id, limit=6)
            context = ChatContext.from_messages(recent_messages, limit=6)

            response = self._llm_provider.generate_response(
                current_message=message,
                available_products=available_products,
                context=context,
            )

            user_message = ChatMessage.create(role="user", content=message)
            assistant_message = ChatMessage.create(role="assistant", content=response)
            self._chat_repository.save_message(session_id, user_message)
            self._chat_repository.save_message(session_id, assistant_message)

            return response, datetime.now(timezone.utc)
        except Exception as exc:  # noqa: BLE001
            raise ChatServiceError(f"Failed to process chat message: {exc}") from exc
