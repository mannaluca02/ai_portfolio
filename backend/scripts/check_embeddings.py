"""
Check if embeddings exist in database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db_session
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_embeddings():
    """Check embeddings in all tables"""
    db = get_db_session()

    try:
        logger.info("Checking embeddings in database...\n")

        tables = [
            'work_experiences',
            'projects',
            'skills',
            'certificates',
            'education',
            'hobbies',
            'contact_info',
            'social_links'
        ]

        for table in tables:
            query = text(f"""
                SELECT
                    COUNT(*) as total,
                    COUNT(embedding) as with_embedding,
                    COUNT(*) - COUNT(embedding) as without_embedding
                FROM {table}
            """)

            result = db.execute(query).fetchone()

            logger.info(f"{table}:")
            logger.info(f"  Total rows: {result.total}")
            logger.info(f"  With embedding: {result.with_embedding}")
            logger.info(f"  Without embedding: {result.without_embedding}")

            # Check if embedding is actually a vector
            if result.with_embedding > 0:
                check_query = text(f"""
                    SELECT
                        id,
                        embedding IS NOT NULL as has_embedding,
                        pg_typeof(embedding) as embedding_type
                    FROM {table}
                    WHERE embedding IS NOT NULL
                    LIMIT 1
                """)
                check_result = db.execute(check_query).fetchone()
                logger.info(f"  Embedding type: {check_result.embedding_type}")

            logger.info("")

        logger.info("✅ Embedding check complete!")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to check embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = check_embeddings()
    sys.exit(0 if success else 1)
