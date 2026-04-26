"""Domain exceptions used across business rules.

Define excepciones personalizadas para errores específicos del dominio.
Permiten capturar y manejar errores de negocio de forma clara y consistente.
Ejemplos: Producto no encontrado, datos inválidos, errores en el chat.
"""


class DomainError(Exception):
    """Base exception for domain errors."""


class ProductNotFoundError(DomainError):
    """Raised when a product does not exist."""


class InvalidProductDataError(DomainError):
    """Raised when product data breaks domain constraints."""


class ChatServiceError(DomainError):
    """Raised when chat processing cannot be completed."""
