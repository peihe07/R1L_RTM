"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import time
import logging

logger = logging.getLogger(__name__)

# PostgreSQL database (production and development)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/requirement_test_db"
)

# Connection arguments (SQLite compatibility maintained for legacy support)
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}


def create_engine_with_retry(database_url, max_retries=5, retry_interval=2):
    """Create database engine with retry mechanism."""
    from sqlalchemy import text

    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url, connect_args=connect_args)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"Database connection established successfully")
            return engine
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}. "
                    f"Retrying in {retry_interval} seconds..."
                )
                time.sleep(retry_interval)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise

    # Fallback (should not reach here)
    return create_engine(database_url, connect_args=connect_args)


engine = create_engine_with_retry(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables."""
    Base.metadata.create_all(bind=engine)