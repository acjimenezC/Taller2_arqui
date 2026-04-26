"""SQL repository implementation for chat memory.

Implementa la interfaz IChatRepository usando SQLAlchemy.
Guarda y recupera el historial de conversaciones de cada sesión.
Retiene los últimos 6 mensajes para proporcionar contexto a la IA.
Ordena los mensajes cronológicamente para mantener la secuencia correcta.
"""

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
        """Inicializa el repositorio de chat.

        Guarda la sesión de SQLAlchemy para operaciones de persistencia
        y recuperación de mensajes.

        Args:
            db: Sesión SQLAlchemy activa.
        """
        self._db = db

    def save_message(self, session_id: str, message: ChatMessage) -> None:
        """Persiste un mensaje del chat en la BD.

        Convierte la entidad ChatMessage a modelo ORM y la guarda
        en la tabla de chat_memory con timestamp de creación.

        Args:
            session_id: Identificador único de la sesión de chat.
            message: Entidad ChatMessage a persistir (usuario o asistente).
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
        """Obtiene los últimos mensajes del chat de una sesión.

        Recupera los N mensajes más recientes en orden cronológico ascendente
        (del más antiguo al más nuevo). Se usa para proporcionar contexto
        a la IA en la ventana de conversación.

        Args:
            session_id: Identificador de la sesión.
            limit: Número máximo de mensajes a retornar (por defecto 6).

        Returns:
            list[ChatMessage]: Lista ordenada de últimos mensajes.
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
        """Obtiene el historial completo del chat de una sesión.

        Recupera TODOS los mensajes de la sesión en orden cronológico
        ascendente desde la más antigua hasta la más reciente.
        Se usa para mostrar el historial completo al usuario.

        Args:
            session_id: Identificador de la sesión.

        Returns:
            list[ChatMessage]: Historial completo ordenado cronológicamente.
        """
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
        """Convierte modelo ORM a entidad de dominio ChatMessage.

        Mapea un registro de la tabla chat_memory a la entidad de dominio.
        Asegura que el timestamp tenga zona horaria UTC.

        Args:
            row: Modelo ORM ChatMemoryModel de SQLAlchemy.

        Returns:
            ChatMessage: Entidad de dominio equivalente.
        """
        created_at = row.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return ChatMessage(role=row.role, content=row.content, created_at=created_at)
