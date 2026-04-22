"""Application data transfer objects."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProductDTO(BaseModel):
    """Product data transfer object used in API input/output."""

    id: int | None = None
    name: str = Field(min_length=1)
    brand: str = Field(min_length=1)
    category: str = Field(min_length=1)
    size: float = Field(gt=0)
    color: str = Field(min_length=1)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    description: str = Field(min_length=1)


class ChatMessageRequestDTO(BaseModel):
    """Incoming request payload for chat endpoint."""

    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)


class ChatMessageResponseDTO(BaseModel):
    """Outgoing response payload for chat endpoint."""

    session_id: str
    response: str
    created_at: datetime


class ChatHistoryItemDTO(BaseModel):
    """Single chat history item."""

    role: str
    content: str
    created_at: datetime
