# Production Dockerfile for FastHTML app
# Builds a slim image that runs uvicorn with the FastHTML/Starlette app.

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

WORKDIR /app

# System deps (build + runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install --upgrade pip && \
    pip install uv && \
    uv sync --no-dev --frozen

# Copy application code
COPY src ./src
COPY README.md ./

# Optional data directory (static assets if present). Do not copy secrets.
COPY data/static ./data/static

# Default command: run the app
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "${PORT}"]

