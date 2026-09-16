"""
Embedding Service - bge-m3 Model
Generates embeddings for text using the bge-m3 model
"""
from sentence_transformers import SentenceTransformer
from app.config import settings
from collections import OrderedDict
from pathlib import Path
from threading import Lock
from typing import List, Union
import logging
import numpy as np

logger = logging.getLogger(__name__)


def _cgroup_cpu_limit() -> int | None:
    """CPUs this container may actually use, or None when no quota is set."""
    try:
        quota, period = Path("/sys/fs/cgroup/cpu.max").read_text().split()
        return None if quota == "max" else max(1, round(int(quota) / int(period)))
    except (OSError, ValueError):
        pass
    try:
        quota = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_quota_us").read_text())
        period = int(Path("/sys/fs/cgroup/cpu/cpu.cfs_period_us").read_text())
        return max(1, round(quota / period)) if quota > 0 and period > 0 else None
    except (OSError, ValueError):
        return None


def configure_torch_threads() -> None:
    """Cap torch's thread pool at the CPUs this process is allowed to use.

    torch sizes the pool from the host's core count, not from the container's
    quota, so on a shared host dozens of threads fight over a fraction of a core
    and batch-size-1 inference turns erratic. Measured against production on one
    identical query, retrieval ran once in 374 ms and once in 12,556 ms.

    TORCH_NUM_THREADS wins when set, 0 derives the limit from the cgroup. The
    count is only ever lowered, so a conservative default is left alone.
    """
    import torch

    limit = settings.TORCH_NUM_THREADS or _cgroup_cpu_limit()
    current = torch.get_num_threads()
    if not limit or current <= limit:
        logger.info("torch threads: %d, no lower limit to apply", current)
        return
    torch.set_num_threads(limit)
    logger.info("torch threads: %d, lowered from %d", limit, current)


class EmbeddingService:
    """Service for generating text embeddings using bge-m3"""
    
    _instance = None
    _model = None
    # Row text does not change between requests, so the verifier re-encoded the
    # same evidence every time. In production that stage cost 3.0-6.2 s per
    # answer against 0.75-0.95 s locally and was the largest share of the 30 s
    # timeouts. Class-level, because __init__ reruns on the singleton.
    _CACHE_SIZE = 512
    _document_cache: "OrderedDict[str, np.ndarray]" = OrderedDict()
    _cache_lock = Lock()

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
        configure_torch_threads()
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
            # No progress bar: this runs per request inside a server process,
            # where the bar is noise in the logs rather than feedback.
            embeddings = self._model.encode(valid_texts, convert_to_numpy=True, show_progress_bar=False)
            return [embedding for embedding in embeddings]
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    def embed_documents(self, texts: List[str]) -> List[np.ndarray]:
        """Embeddings for text that is identical across requests, cached.

        Same vectors as generate_embeddings, only kept. Cache access is locked,
        encoding is not: concurrent misses may encode the same text twice, but
        the returned list is always complete, in order, and never shares arrays
        with the cache.

        Args:
            texts: Deterministic input, such as a portfolio row's evidence text

        Returns:
            List[np.ndarray]: One embedding per input, aligned with texts
        """
        if not texts or any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError("Every embedding input must be a nonempty string")

        unique = list(dict.fromkeys(texts))
        vectors: dict[str, np.ndarray] = {}
        with self._cache_lock:
            for text in unique:
                if text in self._document_cache:
                    vectors[text] = self._document_cache[text]
                    self._document_cache.move_to_end(text)

        missing = [text for text in unique if text not in vectors]
        if missing:
            encoded = self._model.encode(missing, convert_to_numpy=True, show_progress_bar=False)
            fresh = dict(zip(missing, encoded))
            vectors.update(fresh)
            with self._cache_lock:
                for text, vector in fresh.items():
                    self._document_cache[text] = vector
                    self._document_cache.move_to_end(text)
                while len(self._document_cache) > self._CACHE_SIZE:
                    self._document_cache.popitem(last=False)
            logger.info(f"Embedded {len(missing)} of {len(unique)} documents, rest cached")

        return [vectors[text].copy() for text in texts]

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
