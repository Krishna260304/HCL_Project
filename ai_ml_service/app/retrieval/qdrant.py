"""
Qdrant Vector Database Client Manager.
Supports remote Qdrant instances with seamless local in-memory fallback for local development.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from app.core.config import Settings, get_settings
from app.core.exceptions import RetrievalError
from app.schemas.resource import ResourcePayload

logger = logging.getLogger(__name__)


class QdrantManager:
    """Manages Qdrant vector database lifecycle, collections, and CRUD operations."""

    _instance: Optional["QdrantManager"] = None

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.client: Optional[QdrantClient] = None
        self._initialized = False
        self._init_client()

    def _init_client(self) -> None:
        try:
            if self.settings.QDRANT_URL:
                logger.info(f"Connecting to remote Qdrant server at: {self.settings.QDRANT_URL}")
                self.client = QdrantClient(
                    url=self.settings.QDRANT_URL,
                    api_key=self.settings.QDRANT_API_KEY,
                    timeout=self.settings.QDRANT_TIMEOUT,
                )
            else:
                logger.info("Initializing in-memory local Qdrant instance for development/testing.")
                self.client = QdrantClient(location=":memory:")
            self._initialized = True
        except Exception as exc:
            logger.warning(f"Failed to initialize remote Qdrant: {exc}. Falling back to in-memory mode.")
            self.client = QdrantClient(location=":memory:")
            self._initialized = True

    @classmethod
    def get_instance(cls, settings: Optional[Settings] = None) -> "QdrantManager":
        if cls._instance is None:
            cls._instance = cls(settings=settings)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    def is_ready(self) -> bool:
        if not self.client:
            return False
        try:
            self.client.get_collections()
            return True
        except Exception:
            return False

    async def ensure_collection(self, collection_name: Optional[str] = None, vector_size: int = 1024) -> None:
        """Create collection if it does not already exist."""
        coll = collection_name or self.settings.QDRANT_COLLECTION

        def _ensure():
            collections = [c.name for c in self.client.get_collections().collections]
            if coll not in collections:
                logger.info(f"Creating Qdrant collection: {coll} (dim={vector_size})")
                self.client.create_collection(
                    collection_name=coll,
                    vectors_config=rest_models.VectorParams(
                        size=vector_size,
                        distance=rest_models.Distance.COSINE,
                    ),
                )

        await asyncio.to_thread(_ensure)

    async def upsert_resources(
        self,
        resources: List[ResourcePayload],
        embeddings: List[List[float]],
        collection_name: Optional[str] = None,
    ) -> int:
        """Batch upsert resources and embeddings into vector collection."""
        if not resources or not embeddings or len(resources) != len(embeddings):
            return 0

        coll = collection_name or self.settings.QDRANT_COLLECTION
        await self.ensure_collection(coll, vector_size=len(embeddings[0]))

        points = []
        for idx, (res, emb) in enumerate(zip(resources, embeddings)):
            import hashlib
            # Use deterministic integer ID from resource_id string hash
            int_id = int(hashlib.md5(res.resource_id.encode("utf-8")).hexdigest()[:15], 16)
            payload = res.model_dump()
            points.append(
                rest_models.PointStruct(
                    id=int_id,
                    vector=emb,
                    payload=payload,
                )
            )

        def _upsert():
            self.client.upsert(
                collection_name=coll,
                points=points,
                wait=True,
            )

        try:
            await asyncio.to_thread(_upsert)
            return len(points)
        except Exception as e:
            logger.error(f"Failed to upsert points to Qdrant: {e}", exc_info=True)
            raise RetrievalError(f"Vector storage error: {str(e)}")

    async def search_vectors(
        self,
        query_vector: List[float],
        top_k: int = 10,
        collection_name: Optional[str] = None,
        skill_filter: Optional[List[str]] = None,
        difficulty_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search nearest neighbor vectors with optional payload metadata filtering."""
        coll = collection_name or self.settings.QDRANT_COLLECTION
        await self.ensure_collection(coll, vector_size=len(query_vector))

        must_conditions = []
        if difficulty_filter:
            must_conditions.append(
                rest_models.FieldCondition(
                    key="difficulty",
                    match=rest_models.MatchValue(value=difficulty_filter),
                )
            )
        if skill_filter and len(skill_filter) > 0:
            should_skills = [
                rest_models.FieldCondition(key="skills", match=rest_models.MatchValue(value=s))
                for s in skill_filter
            ]
            must_conditions.append(rest_models.Filter(should=should_skills))

        query_filter = rest_models.Filter(must=must_conditions) if must_conditions else None

        def _search():
            try:
                hits = self.client.query_points(
                    collection_name=coll,
                    query=query_vector,
                    limit=top_k,
                    query_filter=query_filter,
                    with_payload=True,
                ).points
            except AttributeError:
                # Fallback to search method if query_points not present in older client versions
                hits = self.client.search(
                    collection_name=coll,
                    query_vector=query_vector,
                    limit=top_k,
                    query_filter=query_filter,
                    with_payload=True,
                )
            return hits

        try:
            results = await asyncio.to_thread(_search)
            formatted = []
            for hit in results:
                payload = getattr(hit, "payload", {}) or {}
                score = getattr(hit, "score", 0.0)
                formatted.append({
                    "id": str(getattr(hit, "id", "")),
                    "score": float(score),
                    "payload": payload,
                })
            return formatted
        except Exception as e:
            logger.error(f"Qdrant vector search failed: {e}", exc_info=True)
            raise RetrievalError(f"Vector search failure: {str(e)}")


def get_qdrant_manager() -> QdrantManager:
    return QdrantManager.get_instance()
