"""
Centralized Embedding Service Singleton.
Loads BGE-M3 model once at application startup and shares it across all workflows.
"""

import logging
from typing import List, Optional
from app.core.config import Settings, get_settings
from app.embeddings.batching import process_in_batches
from app.embeddings.model import BGEM3Provider, EmbeddingProvider, MockEmbeddingProvider

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Singleton service wrapping dense embeddings generation with batching."""

    _instance: Optional["EmbeddingService"] = None

    def __init__(self, provider: Optional[EmbeddingProvider] = None, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        if provider:
            self.provider = provider
        elif self.settings.AI_MOCK_MODE or self.settings.EMBEDDING_PROVIDER == "mock":
            logger.info("Initializing MockEmbeddingProvider")
            self.provider = MockEmbeddingProvider(dimension=self.settings.EMBEDDING_DIMENSION)
        else:
            logger.info(f"Initializing BGEM3Provider ({self.settings.EMBEDDING_MODEL_NAME})")
            self.provider = BGEM3Provider(self.settings)

    @classmethod
    def get_instance(cls, settings: Optional[Settings] = None) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = cls(settings=settings)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    def is_ready(self) -> bool:
        return self.provider.is_ready()

    def get_dimension(self) -> int:
        return self.provider.get_dimension()

    async def embed_query(self, query: str) -> List[float]:
        """Embed a single search query."""
        return await self.provider.embed_query(query)

    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embed a list of documents using configured batch size."""
        if not documents:
            return []

        async def _batch_encode(batch: List[str]) -> List[List[float]]:
            return await self.provider.embed_documents(batch)

        return await process_in_batches(
            items=documents,
            batch_size=self.settings.EMBEDDING_BATCH_SIZE,
            async_processor=_batch_encode,
        )


def get_embedding_service() -> EmbeddingService:
    return EmbeddingService.get_instance()
