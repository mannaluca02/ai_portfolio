from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Base class for all models
Base = declarative_base()


def get_engine():
    """Get database engine instance"""
    return engine


def init_db():
    """Initialize database - create all tables"""
    try:
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def close_db():
    """Close database connections"""
    try:
        logger.info("Closing database connections...")
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
        raise
