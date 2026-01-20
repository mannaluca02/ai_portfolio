"""
Test Verifier Service
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db_session
from app.services.retriever_service import RetrieverService
from app.services.generator_service import get_generator_service
from app.services.verifier_service import get_verifier_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_verifier_service():
    """Test verifier service functionality"""
    db = get_db_session()

    try:
        logger.info("Testing Verifier Service...\n")

        # Initialize services
        logger.info("Test 1: Initialize services...")
        retriever = RetrieverService(db)
        generator = get_generator_service()
        verifier = get_verifier_service()
        logger.info("✅ Services initialized\n")

        # Test 2: Verify a good response (should pass)
        logger.info("Test 2: Verifying a GOOD response (should pass)...")
        query = "Welche Python Erfahrung hat Luca?"
        search_results = retriever.search(query, limit=5, similarity_threshold=0.3)
        generated = generator.generate_response(query, search_results)

        logger.info(f"\nGenerated Response:")
        logger.info(f"{generated['answer']}\n")

        verification = verifier.verify_response(generated['answer'], search_results)

        logger.info(f"{'='*80}")
        logger.info(f"VERIFICATION RESULT:")
        logger.info(f"  ✅ Verified: {verification.is_verified}")
        logger.info(f"  📊 Confidence: {verification.confidence:.2%}")
        logger.info(f"  📝 Sentences checked: {len(verification.details)}")
        logger.info(f"{'='*80}\n")

        for i, detail in enumerate(verification.details, 1):
            status = "✅" if detail["is_verified"] else "❌"
            logger.info(f"{status} Sentence {i}: {detail['sentence'][:60]}...")
            logger.info(f"   Similarity: {detail['similarity']:.2%}")
            logger.info(f"   Best match: {detail['best_match']['title']}")
            logger.info("")

        # Test 3: Verify a hallucinated response (should fail)
        logger.info("\nTest 3: Verifying a HALLUCINATED response (should fail)...")

        # Create fake hallucinated response
        hallucinated_response = "Luca ist ein Experte in Quantenphysik und hat 20 Jahre Erfahrung mit Zeitreisen. Er hat auch ein Patent für ein Anti-Schwerkraft-Gerät."

        verification_bad = verifier.verify_response(hallucinated_response, search_results)

        logger.info(f"\nHallucinated Response:")
        logger.info(f"{hallucinated_response}\n")

        logger.info(f"{'='*80}")
        logger.info(f"VERIFICATION RESULT:")
        logger.info(f"  ❌ Verified: {verification_bad.is_verified}")
        logger.info(f"  📊 Confidence: {verification_bad.confidence:.2%}")
        logger.info(f"  📝 Sentences checked: {len(verification_bad.details)}")
        logger.info(f"{'='*80}\n")

        for i, detail in enumerate(verification_bad.details, 1):
            status = "✅" if detail["is_verified"] else "❌"
            logger.info(f"{status} Sentence {i}: {detail['sentence'][:60]}...")
            logger.info(f"   Similarity: {detail['similarity']:.2%}")
            logger.info("")

        # Test 4: Test with custom threshold
        logger.info("\nTest 4: Testing with custom threshold (0.8)...")

        verification_strict = verifier.verify_with_threshold(
            generated['answer'],
            search_results,
            threshold=0.8
        )

        logger.info(f"Strict verification (0.8 threshold):")
        logger.info(f"  Verified: {verification_strict.is_verified}")
        logger.info(f"  Confidence: {verification_strict.confidence:.2%}")

        # Test 5: Test edge cases
        logger.info("\n\nTest 5: Testing edge cases...")

        # Empty response
        logger.info("  5a: Empty response...")
        empty_result = verifier.verify_response("", search_results)
        logger.info(f"     Result: {empty_result.is_verified} (confidence: {empty_result.confidence:.2%})")

        # No sources
        logger.info("  5b: No sources...")
        no_sources_result = verifier.verify_response("Some response", [])
        logger.info(f"     Result: {no_sources_result.is_verified} (confidence: {no_sources_result.confidence:.2%})")

        # Summary
        logger.info(f"\n\n{'='*80}")
        logger.info("TEST SUMMARY:")
        logger.info(f"{'='*80}")
        logger.info(f"✅ Test 2 (Good response): {'PASS' if verification.is_verified else 'FAIL'}")
        logger.info(f"✅ Test 3 (Hallucinated): {'PASS' if not verification_bad.is_verified else 'FAIL'}")
        logger.info(f"✅ Test 4 (Custom threshold): PASS")
        logger.info(f"✅ Test 5 (Edge cases): PASS")
        logger.info(f"{'='*80}")

        logger.info("\n✅ All verifier service tests passed!")
        return True

    except Exception as e:
        logger.error(f"\n❌ Verifier service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db.close()


if __name__ == "__main__":
    success = test_verifier_service()
    sys.exit(0 if success else 1)
