from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlmodel import select

from src.api.router import setup_routes
from src.core.config import settings
from src.core.database import get_session, init_db
from src.helpers.logger import Logger
from src.helpers.middlewares import LogRequests
from src.models.utils import ServerStatusResponse

logger = Logger(__name__)

async def lifespan(app: FastAPI):  # noqa: ARG001
    try:
        # Startup: ensure database is ready and initialized
        await init_db()
        yield
    except OperationalError as e:
        logger.error(f"Database connection failed during startup: {e}")
        raise OperationalError from e
    except SQLAlchemyError as e:
        logger.error(f"Database error during startup: {e}")
        raise SQLAlchemyError from e
    except Exception as e:
        logger.error(f"Unexpected error during startup: {e}")
        raise e
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
app.include_router(setup_routes(), prefix="/api/v1")

@app.get("/status", response_model=ServerStatusResponse)
async def get_server_status():
    try:
        async with get_session() as session:
            result = await session.execute(
                select(1).execution_options(timeout=10)
            )
            if result.scalar_one() != 1:
                raise SQLAlchemyError("Database health check failed: unexpected response")
            return ServerStatusResponse(
                name=settings.PROJECT_NAME,
                status="healthy",
                database="connected",
                version=settings.VERSION,
                environment=settings.ENV
            )
    except OperationalError as e:
        return ServerStatusResponse(
            name=settings.PROJECT_NAME,
            status="unhealthy",
            database="disconnected",
            version=settings.VERSION,
            environment=settings.ENV,
            error=f"Database connection error: {str(e)}"
        )
    except SQLAlchemyError as e:
        return ServerStatusResponse(
            name=settings.PROJECT_NAME,
            status="unhealthy",
            database="error",
            version=settings.VERSION,
            environment=settings.ENV,
            error=f"Database error: {str(e)}"
        )
    except Exception as e:
        return ServerStatusResponse(
            name=settings.PROJECT_NAME,
            status="unhealthy",
            database="unknown",
            version=settings.VERSION,
            environment=settings.ENV,
            error=f"Unexpected error: {str(e)}"
        )

