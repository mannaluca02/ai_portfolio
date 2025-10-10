"""
Test Generator Service
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db_session
from app.services.retriever_service import RetrieverService
from app.services.generator_service import get_generator_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_generator_service():
    """Test generator service functionality"""
    db = get_db_session()

    try:
        logger.info("Testing Generator Service...\n")

        # Initialize services
        logger.info("Test 1: Initialize services...")
        retriever = RetrieverService(db)
        generator = get_generator_service()
        logger.info("✅ Services initialized\n")

        # Test 2: Generate response for Python skills question
        logger.info("Test 2: Generating response for 'Welche Python Erfahrung hat Luca?'...")

        # First retrieve relevant documents
        query = "Welche Python Erfahrung hat Luca?"
        search_results = retriever.search(query, limit=5, similarity_threshold=0.3)  # Lower threshold for testing
        logger.info(f"   Retrieved {len(search_results)} documents")

        # Generate response
        result = generator.generate_response(query, search_results)

        logger.info(f"\n✅ Response generated!")
        logger.info(f"\n{'='*80}")
        logger.info(f"FRAGE: {query}")
        logger.info(f"{'='*80}")
        logger.info(f"\nANTWORT:\n{result['answer']}")
        logger.info(f"\n{'='*80}")
        logger.info(f"METADATEN:")
        logger.info(f"  - Modus: {result['mode']}")
        logger.info(f"  - Modell: {result['model']}")
        logger.info(f"  - Confidence: {result['confidence']:.2f}")
        logger.info(f"  - Tokens: {result['tokens_used']}")
        logger.info(f"  - Quellen: {len(result['sources'])}")

        logger.info(f"\n{'='*80}")
        logger.info(f"QUELLEN:")
        for source in result['sources']:
            logger.info(f"  [{source['index']}] {source['title']}")
            logger.info(f"      Typ: {source['table']}")
            logger.info(f"      Similarity: {source['similarity']:.2%}")
            logger.info(f"      Link: /{source['slug']}#{source['anchor']}")

        # Test 3: Generate response for React question
        logger.info("\n\nTest 3: Generating response for 'Hat Luca React Erfahrung?'...")

        query2 = "Hat Luca React Erfahrung?"
        search_results2 = retriever.search(query2, limit=5, similarity_threshold=0.3)  # Lower threshold for testing
        result2 = generator.generate_response(query2, search_results2)

        logger.info(f"\n✅ Response generated!")
        logger.info(f"\n{'='*80}")
        logger.info(f"FRAGE: {query2}")
        logger.info(f"{'='*80}")
        logger.info(f"\nANTWORT:\n{result2['answer']}")
        logger.info(f"\n{'='*80}")
        logger.info(f"Confidence: {result2['confidence']:.2f} | Tokens: {result2['tokens_used']} | Quellen: {len(result2['sources'])}")

        # Test 4: Test with no results (edge case)
        logger.info("\n\nTest 4: Testing with query that has no results...")

        query3 = "Kann Luca Quantenphysik?"
        search_results3 = retriever.search(query3, limit=5, similarity_threshold=0.9)  # Very high threshold
        result3 = generator.generate_response(query3, search_results3)

        logger.info(f"\n✅ Response generated!")
        logger.info(f"ANTWORT: {result3['answer']}")
        logger.info(f"Confidence: {result3['confidence']:.2f}")

        logger.info("\n\n✅ All generator service tests passed!")
        return True

    except Exception as e:
        logger.error(f"\n❌ Generator service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_generator_service()
    sys.exit(0 if success else 1)
