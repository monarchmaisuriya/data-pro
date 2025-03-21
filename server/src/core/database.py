import logging
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from sqlmodel import Session, create_engine, select
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import settings

logger = logging.getLogger(__name__)

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
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(OperationalError)
)
def init_db(session: Session) -> None:
    """Initialize database with retry logic for connection failures.
    Args:
        session (Session): SQLModel session object
    Raises:
        OperationalError: If database connection fails after retries
    """
    try:
        # Verify database connection
        session.execute(select(1))
        logger.info("Database connection successful")
    except OperationalError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise
    


