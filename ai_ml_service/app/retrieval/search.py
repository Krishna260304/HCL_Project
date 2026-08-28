"""
Semantic Search Service.
Combines centralized BGE-M3 query embeddings with Qdrant vector retrieval.
"""

import logging
from typing import Any, Dict, List, Optional
from app.embeddings.service import EmbeddingService, get_embedding_service
from app.retrieval.qdrant import QdrantManager, get_qdrant_manager

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """Orchestrates query vectorization and semantic nearest neighbor search."""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        qdrant_manager: Optional[QdrantManager] = None,
    ):
        self.embedding_service = embedding_service or get_embedding_service()
        self.qdrant_manager = qdrant_manager or get_qdrant_manager()

    async def search(
        self,
        query: str,
        top_k: int = 10,
        skill_filter: Optional[List[str]] = None,
        difficulty_filter: Optional[str] = None,
        collection_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Perform semantic search for query text with optional attribute filters."""
        if not query.strip():
            return []

        query_vector = await self.embedding_service.embed_query(query)
        hits = await self.qdrant_manager.search_vectors(
            query_vector=query_vector,
            top_k=top_k,
            collection_name=collection_name,
            skill_filter=skill_filter,
            difficulty_filter=difficulty_filter,
        )
        return hits
