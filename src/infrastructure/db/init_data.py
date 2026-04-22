"""Initial seed data for products."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.db.models import ProductModel


def insert_initial_products(db: Session) -> None:
    """Insert initial product dataset if table is empty.

    Args:
        db: Database session.
    """
    existing = db.execute(select(ProductModel.id)).first()
    if existing:
        return

    products = [
        ProductModel(name="Air Zoom Pegasus", brand="Nike", category="Running", size=41, color="Negro", price=120.0, stock=12, description="Zapatilla running con amortiguacion reactiva."),
        ProductModel(name="Ultraboost Light", brand="Adidas", category="Running", size=42, color="Blanco", price=180.0, stock=8, description="Comodidad premium para entrenamientos largos."),
        ProductModel(name="RS-X", brand="Puma", category="Casual", size=40, color="Gris", price=95.0, stock=15, description="Estilo urbano con suela robusta."),
        ProductModel(name="Chuck Taylor All Star", brand="Converse", category="Casual", size=39, color="Rojo", price=70.0, stock=20, description="Clasico atemporal para uso diario."),
        ProductModel(name="Old Skool", brand="Vans", category="Skate", size=42, color="Negro", price=75.0, stock=11, description="Modelo iconico para skate y streetwear."),
        ProductModel(name="Gel-Kayano 30", brand="ASICS", category="Running", size=43, color="Azul", price=190.0, stock=7, description="Soporte avanzado para pisada pronadora."),
        ProductModel(name="574 Core", brand="New Balance", category="Casual", size=41, color="Verde", price=90.0, stock=10, description="Comodidad y estilo retro en un solo modelo."),
        ProductModel(name="Wave Rider 27", brand="Mizuno", category="Running", size=42, color="Navy", price=140.0, stock=9, description="Equilibrio entre respuesta y estabilidad."),
        ProductModel(name="Forum Low", brand="Adidas", category="Casual", size=40, color="Blanco", price=110.0, stock=13, description="Diseño clasico de baloncesto para diario."),
        ProductModel(name="Court Vision Low", brand="Nike", category="Casual", size=41, color="Blanco", price=85.0, stock=16, description="Inspirada en el estilo basket de los 80."),
        ProductModel(name="Suede Classic", brand="Puma", category="Casual", size=39, color="Azul", price=80.0, stock=14, description="Modelo legendario de ante suave."),
    ]
    db.add_all(products)
    db.commit()
