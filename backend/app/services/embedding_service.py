"""
Embedding Service - bge-m3 Model
Generates embeddings for text using the bge-m3 model
"""
from sentence_transformers import SentenceTransformer
from app.config import settings
from typing import List, Union
import logging
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using bge-m3"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one model instance"""
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the embedding model"""
        if self._model is None:
            self._load_model()
    
    def _load_model(self):
        """Load the bge-m3 model"""
        try:
            logger.info(f"Loading embedding model from {settings.BGE_MODEL_PATH}...")
            self._model = SentenceTransformer(settings.BGE_MODEL_PATH)
            logger.info("✅ Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            # Try loading from HuggingFace as fallback
            try:
                logger.info(f"Attempting to load model from HuggingFace: {settings.BGE_MODEL_NAME}")
                self._model = SentenceTransformer(settings.BGE_MODEL_NAME)
                logger.info("✅ Embedding model loaded from HuggingFace")
            except Exception as e2:
                logger.error(f"❌ Failed to load model from HuggingFace: {e2}")
                raise
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            np.ndarray: Embedding vector (1024 dimensions)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        try:
            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of input texts
            
        Returns:
            List[np.ndarray]: List of embedding vectors
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")
        
        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("No valid texts to embed")
        
        try:
            embeddings = self._model.encode(valid_texts, convert_to_numpy=True, show_progress_bar=True)
            return [embedding for embedding in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            float: Cosine similarity (0-1)
        """
        try:
            # Normalize vectors
            embedding1_norm = embedding1 / np.linalg.norm(embedding1)
            embedding2_norm = embedding2 / np.linalg.norm(embedding2)
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1_norm, embedding2_norm)
            return float(similarity)
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        return self._model.get_sentence_embedding_dimension()


# Global instance
_embedding_service = None


def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
