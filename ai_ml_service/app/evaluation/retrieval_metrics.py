"""
Information Retrieval Evaluation Metrics.
"""

from typing import List, Set


def retrieval_recall_at_k(retrieved_ids: List[str], target_ids: Set[str], k: int) -> float:
    """Calculate retrieval recall at depth K."""
    if not target_ids or not retrieved_ids or k <= 0:
        return 0.0
    hits = sum(1 for item in retrieved_ids[:k] if item in target_ids)
    return round(hits / len(target_ids), 4)


def hit_rate_at_k(retrieved_ids: List[str], target_ids: Set[str], k: int) -> float:
    """Calculate binary Hit Rate at K (1 if at least one relevant item retrieved in top K, else 0)."""
    if not target_ids or not retrieved_ids or k <= 0:
        return 0.0
    for item in retrieved_ids[:k]:
        if item in target_ids:
            return 1.0
    return 0.0
