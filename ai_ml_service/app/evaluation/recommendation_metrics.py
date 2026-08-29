"""
Recommendation Evaluation Metrics.
Calculates Precision@K, Recall@K, Mean Reciprocal Rank (MRR), and NDCG@K.
"""

import math
from typing import List, Set


def precision_at_k(recommended_ids: List[str], ground_truth_relevant_ids: Set[str], k: int) -> float:
    """Calculate Precision@K."""
    if k <= 0 or not recommended_ids or not ground_truth_relevant_ids:
        return 0.0
    top_k = recommended_ids[:k]
    hits = sum(1 for item in top_k if item in ground_truth_relevant_ids)
    return round(hits / k, 4)


def recall_at_k(recommended_ids: List[str], ground_truth_relevant_ids: Set[str], k: int) -> float:
    """Calculate Recall@K."""
    if not ground_truth_relevant_ids or not recommended_ids or k <= 0:
        return 0.0
    top_k = recommended_ids[:k]
    hits = sum(1 for item in top_k if item in ground_truth_relevant_ids)
    return round(hits / len(ground_truth_relevant_ids), 4)


def mean_reciprocal_rank(recommended_ids: List[str], ground_truth_relevant_ids: Set[str]) -> float:
    """Calculate MRR (Mean Reciprocal Rank)."""
    for rank, item in enumerate(recommended_ids, start=1):
        if item in ground_truth_relevant_ids:
            return round(1.0 / rank, 4)
    return 0.0


def ndcg_at_k(recommended_ids: List[str], ground_truth_relevant_ids: Set[str], k: int) -> float:
    """Calculate Normalized Discounted Cumulative Gain at K (NDCG@K) with binary relevance."""
    if k <= 0 or not recommended_ids or not ground_truth_relevant_ids:
        return 0.0

    top_k = recommended_ids[:k]
    dcg = 0.0
    for idx, item in enumerate(top_k):
        if item in ground_truth_relevant_ids:
            dcg += 1.0 / math.log2(idx + 2)  # rank starts at 1, so log2(rank + 1) -> log2(idx + 2)

    # Ideal DCG
    ideal_hits = min(k, len(ground_truth_relevant_ids))
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_hits))

    if idcg == 0.0:
        return 0.0
    return round(dcg / idcg, 4)
