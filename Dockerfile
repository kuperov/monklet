# Frontend: build vendor JS/CSS (gulp outputs to assets/vendor)
FROM node:20-slim AS frontend
WORKDIR /build
COPY src/package.json src/package-lock.json ./
RUN npm ci
COPY src/ ./
RUN npm run build:prod

# App image
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Overlay built static assets so /app/src/assets/vendor exists for collectstatic
COPY --from=frontend /build/assets/vendor /app/src/assets/vendor

ENV DJANGO_SETTINGS_MODULE=config.settings \
    DJANGO_ENVIRONMENT=container \
    DEBUG=False \
    CELERY_BROKER_URL=redis://redis:6379/0 \
    CELERY_RESULT_BACKEND=redis://redis:6379/0 \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    DB_NAME=monklet \
    DB_USER=monklet \
    DB_PASSWORD=monklet \
    DB_HOST=db \
    DB_PORT=5432

CMD ["gunicorn", "config.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "-w", "4"]

