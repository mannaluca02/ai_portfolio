"""
Test database connection
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import engine, get_db_session
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_connection():
    """Test database connection"""
    try:
        logger.info("Testing database connection...")
        
        # Test 1: Create engine and connect
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"✅ Connection successful! Result: {result.scalar()}")
        
        # Test 2: Test session
        db = get_db_session()
        result = db.execute(text("SELECT version()"))
        version = result.scalar()
        logger.info(f"✅ PostgreSQL version: {version}")
        db.close()
        
        # Test 3: Check if pgvector extension exists
        db = get_db_session()
        result = db.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'"))
        has_pgvector = result.fetchone()
        if has_pgvector:
            logger.info("✅ pgvector extension is installed")
        else:
            logger.warning("⚠️  pgvector extension not found!")
        db.close()
        
        logger.info("\n✅ All database tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
