"""FastAPI entrypoint and route definitions.

Define todos los endpoints (rutas) de la API REST:
- GET /health: verifica que el servidor esté funcionando
- GET /products: lista productos con filtros opcionales
- POST /chat: procesa mensajes de usuario con IA y contexto
- GET /chat/history: obtiene el historial completo de un chat
- Operaciones CRUD de productos

Configura CORS para permitir requests desde el frontend.
Inicializa la BD al arrancar la aplicación.
Encadena todas las capas: API -> Servicios -> Repositorios -> BD/IA
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.application.chat_service import ChatService
from src.application.dtos import ChatHistoryItemDTO, ChatMessageRequestDTO, ChatMessageResponseDTO, ProductDTO
from src.application.product_service import ProductService
from src.config import APP_NAME, APP_VERSION
from src.domain.entities import Product
from src.domain.exceptions import InvalidProductDataError, ProductNotFoundError
from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.db.init_data import insert_initial_products
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.infrastructure.repositories.chat_repository import ChatRepository
from src.infrastructure.repositories.product_repository import ProductRepository


app = FastAPI(title=APP_NAME, version=APP_VERSION, description="E-commerce de zapatos con chat inteligente")

# Configurar CORS para permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    """Initialize database and seed minimum products on app startup."""
    init_db()
    db = next(get_db())
    try:
        insert_initial_products(db)
    finally:
        db.close()


@app.get("/health", tags=["Health"], summary="Health check")
def health() -> dict[str, str]:
    """Return API health status.

    Returns:
        dict[str, str]: Health state payload.
    """
    return {"status": "ok"}


@app.get("/products", response_model=list[ProductDTO], tags=["Products"], summary="List and filter products")
def get_products(
    brand: str | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ProductDTO]:
    """List products or filter by brand/category.

    Args:
        brand: Optional brand filter.
        category: Optional category filter.
        db: Database session dependency.

    Returns:
        list[ProductDTO]: Product list.
    """
    service = ProductService(ProductRepository(db))
    products = service.filter_products(brand=brand, category=category) if (brand or category) else service.get_all_products()
    return [ProductDTO.model_validate(product.__dict__) for product in products]


@app.get("/products/{product_id}", response_model=ProductDTO, tags=["Products"], summary="Get product by id")
def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> ProductDTO:
    """Get one product by id.

    Args:
        product_id: Product id.
        db: Database session dependency.

    Returns:
        ProductDTO: Product data.

    Raises:
        HTTPException: If product is not found.
    """
    service = ProductService(ProductRepository(db))
    try:
        product = service.get_product_by_id(product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ProductDTO.model_validate(product.__dict__)


@app.post("/products", response_model=ProductDTO, tags=["Products"], summary="Create product")
def create_product(payload: ProductDTO, db: Session = Depends(get_db)) -> ProductDTO:
    """Create a product.

    Args:
        payload: Product payload.
        db: Database session dependency.

    Returns:
        ProductDTO: Created product.
    """
    service = ProductService(ProductRepository(db))
    entity = Product(**payload.model_dump())
    created = service.create_product(entity)
    return ProductDTO.model_validate(created.__dict__)


@app.put("/products/{product_id}", response_model=ProductDTO, tags=["Products"], summary="Update product")
def update_product(product_id: int, payload: ProductDTO, db: Session = Depends(get_db)) -> ProductDTO:
    """Update a product by id.

    Args:
        product_id: Product id.
        payload: Product data.
        db: Database session dependency.

    Returns:
        ProductDTO: Updated product.
    """
    service = ProductService(ProductRepository(db))
    try:
        entity = Product(**payload.model_dump())
        updated = service.update_product(product_id, entity)
        return ProductDTO.model_validate(updated.__dict__)
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/products/{product_id}", tags=["Products"], summary="Delete product")
def delete_product(product_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    """Delete one product by id.

    Args:
        product_id: Product id.
        db: Database session dependency.

    Returns:
        dict[str, str]: Operation result.
    """
    service = ProductService(ProductRepository(db))
    try:
        service.delete_product(product_id)
        return {"status": "deleted"}
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/chat", response_model=ChatMessageResponseDTO, tags=["Chat"], summary="Send message to AI assistant")
def chat(payload: ChatMessageRequestDTO, db: Session = Depends(get_db)) -> ChatMessageResponseDTO:
    """Process chat message with Gemini and memory context.

    Args:
        payload: Chat request payload.
        db: Database session dependency.

    Returns:
        ChatMessageResponseDTO: Assistant response.

    Raises:
        HTTPException: If chat processing fails.
    """
    service = ChatService(
        product_repository=ProductRepository(db),
        chat_repository=ChatRepository(db),
        llm_provider=GeminiService(),
    )
    try:
        response, created_at = service.process_message(payload.session_id, payload.message)
        return ChatMessageResponseDTO(session_id=payload.session_id, response=response, created_at=created_at)
    except (InvalidProductDataError, Exception) as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/chat/history", response_model=list[ChatHistoryItemDTO], tags=["Chat"], summary="Get full chat history")
def get_chat_history(session_id: str = Query(min_length=1), db: Session = Depends(get_db)) -> list[ChatHistoryItemDTO]:
    """Return complete chat history for a session.

    Args:
        session_id: Chat session id.
        db: Database session dependency.

    Returns:
        list[ChatHistoryItemDTO]: Ordered history items.
    """
    repository = ChatRepository(db)
    history = repository.get_all_messages(session_id)
    return [
        ChatHistoryItemDTO(role=item.role, content=item.content, created_at=item.created_at.astimezone(timezone.utc))
        for item in history
    ]
