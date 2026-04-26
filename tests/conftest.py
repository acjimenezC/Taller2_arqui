"""Shared pytest fixtures.

Configura fixtures reutilizables para todas las pruebas.
Crea una BD en memoria aislada para cada test para evitar contaminación de datos.
Proporciona una sesión de SQLAlchemy limpia para pruebas sin efectos secundarios.
Todas las tablas se crean y se limpian automáticamente para cada test.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.infrastructure.db.database import Base


@pytest.fixture()
def db_session() -> Session:
    """Create isolated in-memory database session for tests.

    Yields:
        Session: SQLAlchemy session.
    """
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
