"""Global application configuration.

Carga variables de entorno desde el archivo .env.
Configura la ruta de la base de datos SQLite.
Define variables globales como nombre y versión de la aplicación.
Guarda claves API para Google Gemini.
Es el punto central de configuración de toda la aplicación.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables desde .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "ecommerce_chat.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH.as_posix()}")

APP_NAME = os.getenv("APP_NAME", "E-Commerce Shoes Chat AI")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
API_PREFIX = os.getenv("API_PREFIX", "")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
