from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.pool import QueuePool
from sqlmodel import Session, SQLModel, create_engine, select
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

# Configure engine with production-grade settings
engine = create_engine(
    str(settings.DATABASE_URL),
    poolclass=QueuePool,
    pool_size=5,  # Number of permanent connections
    max_overflow=10,  # Number of additional connections when pool is full
    pool_timeout=30,  # Seconds to wait for available connection
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Verify connection before using from pool
    echo=settings.ENV == "development"  # SQL logging in development
)

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get a database session with automatic cleanup.
    Yields:
        Session: SQLModel session object
    Raises:
        SQLAlchemyError: If database operations fail
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        session.close()

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=2, min=1, max=30),
    retry=retry_if_exception_type((OperationalError, SQLAlchemyError))
)
def init_db(session: Session) -> None:
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
            SQLModel.metadata.create_all(bind=engine, checkfirst=True)
            logger.info("Tables created successfully.")
        else:
            logger.warning("No tables registered in SQLModel metadata.")

        # Verify database connection with a more precise health check
        result = session.execute(
            select(1).execution_options(timeout=10)
        ).scalar_one()

        if result != 1:
            raise SQLAlchemyError("Database health check failed: unexpected response")

        logger.info("Database initialized successfully - Connection verified")
    except OperationalError as e:
        error_context = {
            "error_type": "connection_error",
            "error_message": str(e),
            "retry_attempt": True
        }
        logger.error(f"Database connection failed: {error_context}")
        raise
    except SQLAlchemyError as e:
        error_context = {
            "error_type": "database_error",
            "error_message": str(e),
            "operation": "initialization"
        }
        logger.error(f"Database error occurred: {error_context}")
        raise



