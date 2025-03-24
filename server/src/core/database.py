from collections.abc import AsyncGenerator

from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
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
async_engine = create_async_engine(
    str(settings.DATABASE_URL),
    poolclass=AsyncAdaptedQueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=60,
    pool_recycle=1800,
    pool_pre_ping=True,
    pool_use_lifo=True,
    connect_args={"timeout": 30}
)

SessionFactory = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async database session with automatic cleanup.
    Yields:
        AsyncSession: SQLModel async session object
    Raises:
        SQLAlchemyError: If database operations fail
    """
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise e
        finally:
            await session.close()

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=1, max=30),
    retry=retry_if_exception_type((OperationalError, SQLAlchemyError))
)
async def init_db() -> None:
    """Initialize database with retry logic for connection failures.
    Raises:
        OperationalError: If database connection fails after retries
        SQLAlchemyError: If any other database error occurs
    """
    try:
        registered_tables = SQLModel.metadata.tables.keys()
        if registered_tables:
            table_names = [table.split('.')[-1] for table in registered_tables]
            logger.info(f"Registered tables: {', '.join(table_names)}")
            # Create database tables with explicit metadata binding without using migrations
            # async with async_engine.begin() as conn:
            #     await conn.run_sync(SQLModel.metadata.create_all)
            # logger.info("Tables created successfully.")
        else:
            logger.warning("No tables registered in SQLModel metadata.")

        # Verify database connection with a health check
        async with SessionFactory() as session:
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
        raise e
    except SQLAlchemyError as e:
        error_context = {
            "error_type": "database_error",
            "error_message": str(e),
            "operation": "initialization"
        }
        logger.error(f"Database error occurred: {error_context}")
        raise e



