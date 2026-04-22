# E-Commerce Shoes Chat AI

Backend en Python con FastAPI, SQLAlchemy, Clean Architecture y chat inteligente con Google Gemini.

## Requisitos

- Docker y Docker Compose
- Opcional: Python 3.11 para ejecucion local

## Variables de entorno

Crea un archivo .env con base en .env.example.

Variables principales:
- APP_NAME
- APP_VERSION
- GEMINI_API_KEY
- GEMINI_MODEL

## Ejecutar con Docker

```bash
docker-compose up --build
```

API disponible en:
- http://localhost:8000
- Swagger: http://localhost:8000/docs

## Endpoints

- GET /health
- GET /products
- GET /products/{id}
- GET /products?brand=...
- GET /products?category=...
- POST /products
- PUT /products/{id}
- DELETE /products/{id}
- POST /chat
- GET /chat/history?session_id=...

## Ejecutar tests

```bash
pytest
```
