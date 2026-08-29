"""
Hybrid Search and Candidate Fusion Service.
Combines dense semantic similarity with sparse keyword signals using Reciprocal Rank Fusion (RRF).
"""

from typing import Any, Dict, List, Optional
from app.retrieval.search import SemanticSearchService
from app.utils.text import extract_keywords


def reciprocal_rank_fusion(
    ranked_lists: List[List[Dict[str, Any]]],
    k: int = 60,
) -> List[Dict[str, Any]]:
    """
    Fuse multiple ranked candidate result lists using Reciprocal Rank Fusion (RRF).
    score(d) = sum_{list} 1 / (k + rank(d))
    """
    scores: Dict[str, float] = {}
    item_map: Dict[str, Dict[str, Any]] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, start=1):
            doc_id = item.get("payload", {}).get("resource_id") or str(item.get("id"))
            item_map[doc_id] = item
            rrf_score = 1.0 / (k + rank)
            scores[doc_id] = scores.get(doc_id, 0.0) + rrf_score

    # Sort fused items by accumulated RRF score
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    fused_results = []
    for doc_id in sorted_ids:
        item_copy = dict(item_map[doc_id])
        item_copy["rrf_score"] = scores[doc_id]
        fused_results.append(item_copy)

    return fused_results


class HybridSearchService:
    """Orchestrates multi-channel retrieval and candidate fusion."""

    def __init__(self, semantic_search: Optional[SemanticSearchService] = None):
        self.semantic_search = semantic_search or SemanticSearchService()

    async def search(
        self,
        query: str,
        top_k: int = 15,
        skill_filter: Optional[List[str]] = None,
        difficulty_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Run dense semantic retrieval and keyword-focused search, then fuse candidates."""
        # 1. Primary dense semantic retrieval
        dense_results = await self.semantic_search.search(
            query=query,
            top_k=top_k,
            skill_filter=skill_filter,
            difficulty_filter=difficulty_filter,
        )

        # 2. Targeted keyword/skill query
        keywords = extract_keywords(query, max_keywords=5)
        sparse_results = []
        if keywords:
            keyword_query = " ".join(keywords)
            sparse_results = await self.semantic_search.search(
                query=keyword_query,
                top_k=top_k,
                skill_filter=skill_filter,
                difficulty_filter=difficulty_filter,
            )

        if not sparse_results:
            return dense_results[:top_k]

        fused = reciprocal_rank_fusion([dense_results, sparse_results], k=60)
        return fused[:top_k]
