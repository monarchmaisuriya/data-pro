# syntax=docker/dockerfile:1.4

# Stage 1: Development stage with debugging tools
FROM python:3.12-slim AS development

ENV COMPOSE_BAKE=true
ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ENV PYTHONPATH=/app

COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/

COPY ./migrations /app/migrations/

COPY ./src /app/src/

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Copy entrypoint script and set permissions
COPY ./entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Stage 2: Production stage
FROM python:3.12-slim AS production

ENV COMPOSE_BAKE=true
ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
ENV UV_LINK_MODE=copy

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ENV PYTHONPATH=/app

COPY ./pyproject.toml ./uv.lock ./alembic.ini /app/

COPY ./migrations /app/migrations/

COPY ./src /app/src/

# Sync the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Copy entrypoint script and set permissions
COPY ./entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]