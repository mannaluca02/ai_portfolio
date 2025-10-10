"""
Test Retriever Service
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db_session
from app.services.retriever_service import RetrieverService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_retriever_service():
    """Test retriever service functionality"""
    db = get_db_session()
    
    try:
        logger.info("Testing Retriever Service...\n")
        
        # Initialize service
        logger.info("Test 1: Initialize retriever service...")
        retriever = RetrieverService(db)
        logger.info("✅ Service initialized\n")
        
        # Test 2: Search for Python skills
        logger.info("Test 2: Searching for 'Python programming experience'...")
        results = retriever.search("Python programming experience", limit=5, similarity_threshold=0.5)
        logger.info(f"✅ Found {len(results)} results")
        
        for i, result in enumerate(results[:3], 1):
            logger.info(f"\n  Result {i}:")
            logger.info(f"    Title: {result.title}")
            logger.info(f"    Table: {result.table}")
            logger.info(f"    Similarity: {result.similarity:.4f}")
            logger.info(f"    Slug: {result.slug}")
        
        # Test 3: Search for React experience
        logger.info("\n\nTest 3: Searching for 'React frontend development'...")
        results = retriever.search("React frontend development", limit=5, similarity_threshold=0.5)
        logger.info(f"✅ Found {len(results)} results")
        
        for i, result in enumerate(results[:3], 1):
            logger.info(f"\n  Result {i}:")
            logger.info(f"    Title: {result.title}")
            logger.info(f"    Table: {result.table}")
            logger.info(f"    Similarity: {result.similarity:.4f}")
        
        # Test 4: Search specific tables only
        logger.info("\n\nTest 4: Searching only in 'work_experiences' and 'projects'...")
        results = retriever.search(
            "Full-Stack Developer", 
            limit=3, 
            similarity_threshold=0.5,
            tables=['work_experiences', 'projects']
        )
        logger.info(f"✅ Found {len(results)} results")
        
        for i, result in enumerate(results, 1):
            logger.info(f"\n  Result {i}:")
            logger.info(f"    Title: {result.title}")
            logger.info(f"    Table: {result.table}")
            logger.info(f"    Similarity: {result.similarity:.4f}")
        
        # Test 5: Test with low threshold
        logger.info("\n\nTest 5: Testing with high threshold (0.8)...")
        results = retriever.search("Machine Learning", limit=5, similarity_threshold=0.8)
        logger.info(f"✅ Found {len(results)} high-quality results")
        
        logger.info("\n\n✅ All retriever service tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Retriever service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    success = test_retriever_service()
    sys.exit(0 if success else 1)
