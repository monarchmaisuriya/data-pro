from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlmodel import SQLModel, select
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

import src.models  # noqa: F401
from src.core.config import settings
from src.helpers.logger import Logger

logger = Logger(__name__)

# Configure async engine with production-grade settings
engine = create_async_engine(
    str(settings.DATABASE_URL),
    poolclass=AsyncAdaptedQueuePool,
    pool_size=5,  # Number of permanent connections
    max_overflow=10,  # Number of additional connections when pool is full
    pool_timeout=30,  # Seconds to wait for available connection
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Verify connection before using from pool
    echo=settings.ENV == "development"  # SQL logging in development
)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session with automatic cleanup.
    Yields:
        AsyncSession: SQLModel async session object
    Raises:
        SQLAlchemyError: If database operations fail
    """
    session = AsyncSession(engine)
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        await session.close()

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=1, max=30),
    retry=retry_if_exception_type((OperationalError, SQLAlchemyError))
)
async def init_db(session: AsyncSession) -> None:
    """Initialize database with retry logic for connection failures.
    Args:
        session (Session): SQLModel session object
    Raises:
        OperationalError: If database connection fails after retries
        SQLAlchemyError: If any other database error occurs
    """
    try:
        registered_tables = SQLModel.metadata.tables.keys()
        if registered_tables:
            logger.info(f"Registered tables: {registered_tables}")
            # Create database tables with explicit metadata binding
            # Use engine.sync_engine for table creation since SQLModel's create_all expects a sync engine
            await session.run_sync(lambda s: SQLModel.metadata.create_all(bind=engine.sync_engine, checkfirst=True))
            logger.info("Tables created successfully.")
        else:
            logger.warning("No tables registered in SQLModel metadata.")

        # Verify database connection with a more precise health check
        result = await session.execute(
            select(1).execution_options(timeout=10)
        )
        if result.scalar_one() != 1:
            raise SQLAlchemyError("Database health check failed: unexpected response")

        logger.info("Database initialized successfully - Connection verified")
    except OperationalError as e:
        error_context = {
            "error_type": "connection_error",
            "error_message": str(e),
            "retry_attempt": True
        }
        logger.error(f"Database connection failed: {error_context}")
        raise OperationalError(f"Database connection failed: {error_context}")
    except SQLAlchemyError as e:
        error_context = {
            "error_type": "database_error",
            "error_message": str(e),
            "operation": "initialization"
        }
        logger.error(f"Database error occurred: {error_context}")
        raise SQLAlchemyError(f"Database error occurred: {error_context}")



