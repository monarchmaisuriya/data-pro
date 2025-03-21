from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, text

from src.core.config import settings
from src.core.database import engine, init_db

# from api.v1 import router as api_v1_router
from src.helpers.middlewares import LogRequests


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    try:
        # Startup: ensure database is ready and initialized
        with Session(engine) as session:
            init_db(session)
        yield
    finally:
        session.close()
        # No need to explicitly dispose since SQLModel handles connection pooling

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Configure middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(LogRequests)

# Include API routers
# app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/status")
def get_server_status():
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
            return {"name": settings.PROJECT_NAME,
                    "status": "healthy",
                    "database": "connected",
                    "version": settings.VERSION,
                    "environment": settings.ENV,
                    }
    except Exception as e:
        return {"name": settings.PROJECT_NAME,
                "status": "unhealthy",
                "database": "disconnected",
                "version": settings.VERSION,
                "environment": settings.ENV,
                "error": str(e)}

