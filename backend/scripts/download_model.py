"""
Download bge-m3 embedding model
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sentence_transformers import SentenceTransformer
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_model():
    """Download bge-m3 model"""
    try:
        logger.info(f"Downloading model: {settings.BGE_MODEL_NAME}")
        logger.info(f"Target path: {settings.BGE_MODEL_PATH}")
        
        # Create directory if it doesn't exist
        model_dir = Path(settings.BGE_MODEL_PATH)
        model_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Download and cache model
        logger.info("This may take a few minutes (model size: ~2.2 GB)...")
        model = SentenceTransformer(settings.BGE_MODEL_NAME)
        
        # Save model to custom path
        logger.info(f"Saving model to {settings.BGE_MODEL_PATH}...")
        model.save(settings.BGE_MODEL_PATH)
        
        logger.info("✅ Model downloaded and saved successfully!")
        
        # Test model
        logger.info("\nTesting model...")
        test_text = "This is a test sentence."
        embedding = model.encode(test_text)
        
        logger.info(f"✅ Model test successful!")
        logger.info(f"   Embedding dimensions: {len(embedding)}")
        logger.info(f"   Expected: 1024")
        
        if len(embedding) == 1024:
            logger.info("\n✅ All checks passed! Model is ready to use.")
            return True
        else:
            logger.error(f"\n❌ Embedding dimension mismatch! Expected 1024, got {len(embedding)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to download model: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)
