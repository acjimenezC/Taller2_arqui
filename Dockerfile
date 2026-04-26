# Dockerfile - Containeriza la aplicación Python
# Construye una imagen Docker que ejecuta la API FastAPI en un contenedor.
# Usa Python 3.11 slim para minimizar el tamaño de la imagen.
# Instala dependencias desde requirements.txt y expone el puerto 8000.
# Se usa con docker-compose para orquestar con el frontend.

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
