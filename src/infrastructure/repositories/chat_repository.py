"""SQL repository implementation for chat memory."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel


class ChatRepository(IChatRepository):
    """SQLAlchemy implementation of chat repository."""

    def __init__(self, db: Session) -> None:
        """Store database session.

        Args:
            db: SQLAlchemy session.
        """
        self._db = db

    def save_message(self, session_id: str, message: ChatMessage) -> None:
        """Persist one chat message.

        Args:
            session_id: Session identifier.
            message: Message entity.
        """
        model = ChatMemoryModel(
            session_id=session_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )
        self._db.add(model)
        self._db.commit()

    def get_recent_messages(self, session_id: str, limit: int = 6) -> list[ChatMessage]:
        """Return latest chat messages in chronological order.

        Args:
            session_id: Session identifier.
            limit: Message limit.

        Returns:
            list[ChatMessage]: Latest messages.
        """
        rows = (
            self._db.execute(
                select(ChatMemoryModel)
                .where(ChatMemoryModel.session_id == session_id)
                .order_by(ChatMemoryModel.created_at.desc(), ChatMemoryModel.id.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )
        rows.reverse()
        return [self._to_entity(row) for row in rows]

    def get_all_messages(self, session_id: str) -> list[ChatMessage]:
        """Return complete chat history for one session."""
        rows = (
            self._db.execute(
                select(ChatMemoryModel)
                .where(ChatMemoryModel.session_id == session_id)
                .order_by(ChatMemoryModel.created_at.asc(), ChatMemoryModel.id.asc())
            )
            .scalars()
            .all()
        )
        return [self._to_entity(row) for row in rows]

    @staticmethod
    def _to_entity(row: ChatMemoryModel) -> ChatMessage:
        """Map ORM row to domain entity."""
        created_at = row.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return ChatMessage(role=row.role, content=row.content, created_at=created_at)
