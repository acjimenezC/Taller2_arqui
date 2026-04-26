# 🛒 E-Commerce Shoes Chat AI

Backend inteligente para tienda de zapatos con chat IA conversacional.

**Tecnologías:** Python 3.11, FastAPI, SQLAlchemy, SQLite, Google Gemini, Docker, Clean Architecture

---

## 📋 Tabla de Contenidos

1. [Requisitos](#requisitos)
2. [Instalación](#instalación)
3. [Configuración](#configuración)
4. [Ejecución](#ejecución)
5. [API Endpoints](#api-endpoints)
6. [Estructura del Proyecto](#estructura-del-proyecto)
7. [Testing](#testing)
8. [Ejemplos de Uso](#ejemplos-de-uso)

---

## 📦 Requisitos

### Docker (Recomendado)
- Docker Desktop o Docker CLI
- Docker Compose

### Local (Alternativo)
- Python 3.11+
- pip (gestor de paquetes)
- Git

---

## 🚀 Instalación

### Opción 1: Con Docker (RECOMENDADO)

```bash
# 1. Clonar repositorio
git clone https://github.com/usuario/e-commerce-chat-ai.git
cd e-commerce-chat-ai

# 2. Crear archivo .env
cp .env.example .env

# 3. Ejecutar con Docker
docker-compose up --build
```

### Opción 2: Instalación Local

```bash
# 1. Clonar repositorio
git clone https://github.com/usuario/e-commerce-chat-ai.git
cd e-commerce-chat-ai

# 2. Crear ambiente virtual
python -m venv .venv

# 3. Activar ambiente (Windows)
.venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Crear archivo .env
cp .env.example .env

# 6. Ejecutar aplicación
python -m uvicorn src.infrastructure.api.main:app --reload
```

---

## 🔑 Configuración (.env)

Crea un archivo `.env` en la raíz del proyecto:

```env
APP_NAME=E-Commerce Shoes Chat AI
APP_VERSION=1.0.0
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
GEMINI_API_KEY=tu_clave_aqui
GEMINI_MODEL=gemini-1.5-flash
```

### Obtener GEMINI_API_KEY

1. Visita [Google AI Studio](https://aistudio.google.com/)
2. Crea una cuenta o inicia sesión
3. Click en "Create API Key"
4. Copia la clave y pégala en `.env`

---

## ▶️ Ejecución

### Con Docker
```bash
docker-compose up --build
```

### Local con reload
```bash
python -m uvicorn src.infrastructure.api.main:app --reload
```

### Local sin reload
```bash
python -m uvicorn src.infrastructure.api.main:app --host 0.0.0.0 --port 8000
```

**La API estará disponible en:** `http://localhost:8000`

**Documentación interactiva:** `http://localhost:8000/docs`

---

## 📡 API Endpoints

### Health
- **GET** `/health` - Verifica que la API esté funcionando

### Productos
- **GET** `/products` - Lista todos los productos
- **GET** `/products/{product_id}` - Obtiene un producto específico
- **GET** `/products?brand=Nike` - Filtra por marca
- **GET** `/products?category=Running` - Filtra por categoría
- **POST** `/products` - Crea un nuevo producto
- **PUT** `/products/{product_id}` - Actualiza un producto
- **DELETE** `/products/{product_id}` - Elimina un producto

### Chat con IA
- **POST** `/chat` - Envía mensaje y recibe respuesta de la IA
- **GET** `/chat/history?session_id=xxx` - Obtiene historial de chat

---

## 🏗️ Estructura del Proyecto

```
e-commerce-chat-ai/
├── src/
│   ├── application/          # Casos de uso y servicios
│   │   ├── chat_service.py
│   │   ├── product_service.py
│   │   └── dtos.py
│   ├── domain/               # Lógica de negocio pura
│   │   ├── entities.py
│   │   ├── exceptions.py
│   │   └── repositories.py
│   ├── infrastructure/       # Implementación técnica
│   │   ├── api/
│   │   │   └── main.py      # Endpoints FastAPI
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── init_data.py
│   │   ├── llm_providers/
│   │   │   └── gemini_service.py
│   │   └── repositories/
│   │       ├── product_repository.py
│   │       └── chat_repository.py
│   └── config.py             # Configuración global
├── tests/                    # Pruebas unitarias
├── frontend/                 # Interfaz web
├── data/                     # Base de datos SQLite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

### Capas de Clean Architecture

- **Domain:** Entidades, excepciones, contratos
- **Application:** Servicios, DTOs, casos de uso
- **Infrastructure:** BD, APIs externas, repositorios

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con salida detallada
pytest -v

# Con cobertura
pytest --cov=src --cov-report=html

# Test específico
pytest tests/test_api.py::test_health_endpoint -v
```

---

## 💡 Ejemplos de Uso

### 1. Obtener todos los productos

```bash
curl http://localhost:8000/products
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "name": "Air Zoom Pegasus",
    "brand": "Nike",
    "category": "Running",
    "size": 41,
    "color": "Negro",
    "price": 120.0,
    "stock": 12,
    "description": "Zapatilla running con amortiguacion reactiva."
  },
  ...
]
```

### 2. Buscar productos por marca

```bash
curl "http://localhost:8000/products?brand=Nike"
```

### 3. Usar el chat con IA

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user-123",
    "message": "¿Tienes zapatos Nike para correr?"
  }'
```

**Respuesta:**
```json
{
  "session_id": "user-123",
  "response": "¡Excelente! Tenemos zapatos Nike perfecto para correr...",
  "created_at": "2026-04-26T19:30:00Z"
}
```

### 4. Obtener historial de chat

```bash
curl "http://localhost:8000/chat/history?session_id=user-123"
```

---

## 🔧 Troubleshooting

### Error: ModuleNotFoundError: No module named 'src'
```bash
# Asegúrate de estar en la carpeta correcta
cd e-commerce-chat-ai

# Activa el virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### Error: GEMINI_API_KEY no configurada
- Verifica que `GEMINI_API_KEY` está en el archivo `.env`
- Obtén una clave en [Google AI Studio](https://aistudio.google.com/)

### Docker no encuentra el contenedor
```bash
# Ver contenedores activos
docker ps

# Ver logs
docker logs ecommerce-chat-ai
```

---

## 📚 Documentación Adicional

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Google Gemini API](https://ai.google.dev/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

## 👨‍💻 Autor

Proyecto desarrollado como taller de Construcción de E-commerce con Chat IA - Universidad EAFIT

---

## 📄 Licencia

MIT License
