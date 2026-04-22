"""Domain exceptions used across business rules."""


class DomainError(Exception):
    """Base exception for domain errors."""


class ProductNotFoundError(DomainError):
    """Raised when a product does not exist."""


class InvalidProductDataError(DomainError):
    """Raised when product data breaks domain constraints."""


class ChatServiceError(DomainError):
    """Raised when chat processing cannot be completed."""
