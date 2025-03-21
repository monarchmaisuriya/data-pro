# syntax=docker/dockerfile:1.4

# Stage 1: Development stage with debugging tools
FROM python:3.12-slim AS development

ENV COMPOSE_BAKE=true
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Install development dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir uv

# Copy dependency files and install the dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync 

# Copy application code
COPY . .

EXPOSE 8000

# Start development server with FastAPI CLI
CMD ["uv", "run", "fastapi", "dev", "--host", "0.0.0.0", "--port", "8000", "/app/src/main.py"]

# Stage 2: Production stage
FROM python:3.12-slim AS production

ENV COMPOSE_BAKE=true
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files and install the dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync 

# Copy application code
COPY . .

EXPOSE 8000

# Start production server with FastAPI CLI
CMD ["uv", "run", "fastapi", "run", "--host", "0.0.0.0", "--port", "8000", "/app/src/main.py"]

