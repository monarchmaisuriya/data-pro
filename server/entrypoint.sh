#!/bin/sh

# Get TARGET from environment variable, default to development if not set
TARGET=${TARGET:-development}

# Run database migrations
echo "Running database migrations..."
uv run alembic upgrade head

# Start the application based on environment
if [ "$TARGET" = "development" ]; then
    echo "Starting FastAPI in development mode..."
    exec uv run fastapi dev --host 0.0.0.0 --port 8000 /app/src/main.py
else
    echo "Starting FastAPI in production mode..."
    exec uv run fastapi run --host 0.0.0.0 --port 8000 /app/src/main.py
fi