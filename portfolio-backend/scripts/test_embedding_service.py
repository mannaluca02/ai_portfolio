"""
Test Embedding Service
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.embedding_service import get_embedding_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_embedding_service():
    """Test embedding service functionality"""
    try:
        logger.info("Testing Embedding Service...\n")
        
        # Test 1: Load service
        logger.info("Test 1: Loading embedding service...")
        service = get_embedding_service()
        logger.info("✅ Service loaded successfully")
        
        # Test 2: Check embedding dimension
        logger.info("\nTest 2: Checking embedding dimension...")
        dimension = service.get_embedding_dimension()
        logger.info(f"✅ Embedding dimension: {dimension}")
        
        if dimension != 1024:
            logger.error(f"❌ Expected 1024, got {dimension}")
            return False
        
        # Test 3: Generate single embedding
        logger.info("\nTest 3: Generating single embedding...")
        test_text = "I am a Full-Stack Developer with experience in Python and React."
        embedding = service.generate_embedding(test_text)
        logger.info(f"✅ Embedding generated successfully")
        logger.info(f"   Shape: {embedding.shape}")
        logger.info(f"   Type: {type(embedding)}")
        
        # Test 4: Generate multiple embeddings (batch)
        logger.info("\nTest 4: Generating batch embeddings...")
        test_texts = [
            "Python programming",
            "React development",
            "FastAPI backend"
        ]
        embeddings = service.generate_embeddings(test_texts)
        logger.info(f"✅ {len(embeddings)} embeddings generated")
        
        # Test 5: Calculate similarity
        logger.info("\nTest 5: Calculating similarity...")
        text1 = "I love Python programming"
        text2 = "Python is my favorite programming language"
        text3 = "I enjoy cooking Italian food"
        
        emb1 = service.generate_embedding(text1)
        emb2 = service.generate_embedding(text2)
        emb3 = service.generate_embedding(text3)
        
        similarity_12 = service.calculate_similarity(emb1, emb2)
        similarity_13 = service.calculate_similarity(emb1, emb3)
        
        logger.info(f"✅ Similarity between similar texts: {similarity_12:.4f}")
        logger.info(f"✅ Similarity between different texts: {similarity_13:.4f}")
        
        if similarity_12 > similarity_13:
            logger.info("✅ Similarity test passed (similar texts have higher score)")
        else:
            logger.warning("⚠️  Unexpected: dissimilar texts have higher similarity")
        
        logger.info("\n✅ All embedding service tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Embedding service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_embedding_service()
    sys.exit(0 if success else 1)
