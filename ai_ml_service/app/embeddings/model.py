"""
Embedding Provider Interface and Implementations.
Default model: BAAI/bge-m3 (1024 dimensions).
"""

from abc import ABC, abstractmethod
import asyncio
import logging
from typing import Any, List, Optional
import numpy as np
from app.core.config import Settings, get_settings
from app.core.exceptions import ModelInferenceError

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract interface for swappable embedding models."""

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compute dense vector embeddings for a list of document strings."""
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Compute dense vector embedding for a single query string."""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return embedding vector dimensionality."""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """Check if embedding model is loaded."""
        pass


class BGEM3Provider(EmbeddingProvider):
    """
    BAAI/bge-m3 dense embedding provider using SentenceTransformers.
    Optimized for multi-lingual, multi-granularity dense representations.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.dimension = settings.EMBEDDING_DIMENSION
        self.model = None
        self._initialized = False
        self._lock = asyncio.Lock()

    def _load_model_sync(self) -> None:
        if self._initialized:
            return

        import torch
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading BGE-M3 Embedding model: {self.model_name}")
        if self.settings.EMBEDDING_DEVICE != "cuda":
            raise RuntimeError("EMBEDDING_DEVICE must be set to 'cuda' for production inference.")
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is unavailable; refusing to load embeddings on CPU.")
        device = "cuda"
        self.model = SentenceTransformer(self.model_name, device=device)
        self._initialized = True
        logger.info(f"BGE-M3 model initialized on device: {device}")

    async def ensure_loaded(self) -> None:
        if not self._initialized:
            async with self._lock:
                if not self._initialized:
                    await asyncio.to_thread(self._load_model_sync)

    def is_ready(self) -> bool:
        return self._initialized

    def get_dimension(self) -> int:
        return self.dimension

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        await self.ensure_loaded()

        def _encode_sync():
            embeddings = self.model.encode(
                texts,
                batch_size=self.settings.EMBEDDING_BATCH_SIZE,
                show_progress_bar=False,
                normalize_embeddings=True,
            )
            return embeddings.tolist()

        try:
            return await asyncio.to_thread(_encode_sync)
        except Exception as exc:
            logger.error(f"Embedding encoding failed: {str(exc)}", exc_info=True)
            raise ModelInferenceError(f"Embedding failure: {str(exc)}")

    async def embed_query(self, text: str) -> List[float]:
        results = await self.embed_documents([text])
        return results[0] if results else [0.0] * self.dimension


class MockEmbeddingProvider(EmbeddingProvider):
    """
    Deterministic Mock Embedding Provider for fast CPU-only tests and CI.
    Generates reproducible 1024-dimensional normalized vectors from text hashes.
    """

    def __init__(self, dimension: int = 1024):
        self.dimension = dimension

    def is_ready(self) -> bool:
        return True

    def get_dimension(self) -> int:
        return self.dimension

    def _hash_to_vector(self, text: str) -> List[float]:
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Seed pseudo-random generator deterministically from hash
        seed = int.from_bytes(h[:4], "big")
        rng = np.random.RandomState(seed)
        vec = rng.randn(self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._hash_to_vector(t) for t in texts]

    async def embed_query(self, text: str) -> List[float]:
        return self._hash_to_vector(text)
