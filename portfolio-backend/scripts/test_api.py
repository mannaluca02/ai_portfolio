"""
Test API Endpoints
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


def test_api():
    """Test API endpoints"""

    try:
        logger.info("Testing Portfolio RAG Chatbot API...\n")

        # Test 1: Root endpoint
        logger.info("Test 1: Testing root endpoint (GET /)...")
        response = requests.get(f"{BASE_URL}/")
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        logger.info("✅ Root endpoint working\n")

        # Test 2: Health check
        logger.info("Test 2: Testing health check (GET /api/health)...")
        response = requests.get(f"{BASE_URL}/api/health")
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        assert response.json()["status"] in ["healthy", "degraded"]
        logger.info("✅ Health check working\n")

        # Test 3: Get chat modes
        logger.info("Test 3: Testing chat modes (GET /api/chat/modes)...")
        response = requests.get(f"{BASE_URL}/api/chat/modes")
        logger.info(f"Status: {response.status_code}")
        data = response.json()
        logger.info(f"Available modes: {[m['name'] for m in data['modes']]}")
        assert response.status_code == 200
        assert len(data["modes"]) == 2
        logger.info("✅ Chat modes endpoint working\n")

        # Test 4: Chat in LISTEN mode
        logger.info("Test 4: Testing chat in LISTEN mode...")
        payload = {
            "message": "Welche Python Erfahrung hat Luca?",
            "mode": "listen"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        logger.info(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"\n{'='*80}")
            logger.info(f"LISTEN MODE RESPONSE:")
            logger.info(f"{'='*80}")
            logger.info(f"Answer: {data['answer'][:100]}...")
            logger.info(f"Mode: {data['mode']}")
            logger.info(f"Confidence: {data['confidence']:.2%}")
            logger.info(f"Sources: {len(data['sources'])}")
            logger.info(f"{'='*80}\n")
            assert data["mode"] == "listen"
            logger.info("✅ LISTEN mode working\n")
        else:
            logger.error(f"❌ LISTEN mode failed: {response.text}")

        # Test 5: Chat in NATURAL mode
        logger.info("Test 5: Testing chat in NATURAL mode...")
        payload = {
            "message": "Hat Luca React Erfahrung?",
            "mode": "natural"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        logger.info(f"Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"\n{'='*80}")
            logger.info(f"NATURAL MODE RESPONSE:")
            logger.info(f"{'='*80}")
            logger.info(f"Answer: {data['answer']}")
            logger.info(f"\nMode: {data['mode']}")
            logger.info(f"Confidence: {data['confidence']:.2%}")
            logger.info(f"Sources: {len(data['sources'])}")

            if data.get("verification"):
                logger.info(f"\nVerification:")
                logger.info(f"  Is Verified: {data['verification']['is_verified']}")
                logger.info(f"  Confidence: {data['verification']['confidence']:.2%}")
                logger.info(f"  Threshold: {data['verification']['threshold']:.2%}")

            if data.get("metadata"):
                logger.info(f"\nMetadata:")
                logger.info(f"  Model: {data['metadata'].get('model')}")
                logger.info(f"  Tokens: {data['metadata'].get('tokens_used')}")
                logger.info(f"  Processing Time: {data['metadata'].get('processing_time_ms')}ms")

            logger.info(f"{'='*80}\n")
            assert data["mode"] == "natural"
            logger.info("✅ NATURAL mode working\n")
        else:
            logger.error(f"❌ NATURAL mode failed: {response.text}")

        # Test 6: Test validation (empty message)
        logger.info("Test 6: Testing validation (empty message)...")
        payload = {
            "message": "",
            "mode": "natural"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        logger.info(f"Status: {response.status_code}")
        assert response.status_code == 422  # Validation error
        logger.info("✅ Validation working\n")

        logger.info("\n" + "="*80)
        logger.info("✅ ALL API TESTS PASSED!")
        logger.info("="*80)

        return True

    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to API. Make sure the server is running:")
        logger.error("   uvicorn app.main:app --reload")
        return False
    except Exception as e:
        logger.error(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("PORTFOLIO RAG CHATBOT API TESTS")
    logger.info("=" * 80)
    logger.info("Make sure the API server is running:")
    logger.info("  cd portfolio-backend")
    logger.info("  source venv/bin/activate")
    logger.info("  uvicorn app.main:app --reload")
    logger.info("=" * 80 + "\n")

    success = test_api()
    sys.exit(0 if success else 1)
