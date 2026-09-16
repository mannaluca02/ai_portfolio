"""Opt-in embedding adapter; never use these vectors with the BGE index.

Not wired into the application factory until versioned corpus storage is ready.
The caller owns the injected OpenAI client and its lifecycle. No settings or
credential files are loaded here. Calls are synchronous, like the BGE interface.
"""

from collections import OrderedDict
from threading import Lock

import numpy as np
from openai import OpenAI


class OpenAIEmbeddingService:
    """Fixed embedding space with a bounded, process-local query cache."""

    model = "text-embedding-3-small"
    dimensions = 1024
    space_id = "openai:text-embedding-3-small:1024"

    def __init__(self, client: OpenAI, *, cache_size: int = 256, timeout: float = 5.0):
        if cache_size < 0 or not np.isfinite(timeout) or timeout <= 0:
            raise ValueError("Invalid embedding cache size or timeout")
        self._client = client.with_options(timeout=timeout, max_retries=0)
        self._cache_size = cache_size
        self._cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self._lock = Lock()

    def _vector(self, value) -> np.ndarray:
        vector = np.asarray(value, dtype=np.float64)
        if vector.shape != (self.dimensions,) or not np.isfinite(vector).all():
            raise ValueError("Invalid embedding dimensions or values")
        norm = np.linalg.norm(vector)
        if not np.isfinite(norm) or norm == 0:
            raise ValueError("Invalid embedding magnitude")
        return vector.copy()

    def generate_embedding(self, text: str) -> np.ndarray:
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: list[str]) -> list[np.ndarray]:
        """Deduplicate requests without losing row alignment or sharing arrays.

        Cache access is locked, network requests are not. Concurrent misses may
        issue duplicate requests, but cannot corrupt the cache. An invalid batch
        is rejected atomically and never inserted into the cache.
        """
        if not texts or any(not isinstance(t, str) or not t.strip() for t in texts):
            raise ValueError("Every embedding input must be a nonempty string")
        unique = list(dict.fromkeys(texts))
        vectors: dict[str, np.ndarray] = {}
        with self._lock:
            for text in unique:
                if text in self._cache:
                    vectors[text] = self._cache[text]
                    self._cache.move_to_end(text)
        missing = [text for text in unique if text not in vectors]
        if missing:
            result = self._client.embeddings.create(
                model=self.model, dimensions=self.dimensions,
                encoding_format="float", input=missing,
            )
            if result.model != self.model or len(result.data) != len(missing):
                raise ValueError("Embedding model or response count mismatch")
            received: dict[int, np.ndarray] = {}
            for item in result.data:
                if (type(item.index) is not int or item.index in received
                        or not 0 <= item.index < len(missing)):
                    raise ValueError("Invalid embedding response index")
                received[item.index] = self._vector(item.embedding)
            fresh = {text: received[i] for i, text in enumerate(missing)}
            vectors.update(fresh)
            with self._lock:
                for text, vector in fresh.items():
                    self._cache[text] = vector
                    self._cache.move_to_end(text)
                while len(self._cache) > self._cache_size:
                    self._cache.popitem(last=False)
        return [vectors[text].copy() for text in texts]

    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        first, second = self._vector(embedding1), self._vector(embedding2)
        return float(np.clip(np.dot(first / np.linalg.norm(first),
                                    second / np.linalg.norm(second)), -1, 1))

    def get_embedding_dimension(self) -> int:
        return self.dimensions
