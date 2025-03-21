from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlmodel import text

from src.core.config import settings
from src.core.database import get_session, init_db
from src.helpers.logger import Logger

# from api.v1 import router as api_v1_router
from src.helpers.middlewares import LogRequests

logger = Logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    try:
        # Startup: ensure database is ready and initialized
        async with get_session() as session:
            await init_db(session)
            logger.info("Database initialized successfully during startup")
        yield
    except OperationalError as e:
        logger.error(f"Database connection failed during startup: {e}")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during startup: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during startup: {e}")
        raise
    finally:
        # Cleanup will be handled by SQLModel's connection pooling
        logger.info("Application shutdown - Database connections will be cleaned up")

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
async def get_server_status():
    try:
        async with get_session() as session:
            result = await session.execute(text("SELECT 1"))
            await result.scalar_one()
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

