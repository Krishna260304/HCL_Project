"""
Tests for Vector Storage, Qdrant in-memory mode, Hybrid Search, and Reranking.
"""

import pytest
from app.embeddings.service import get_embedding_service
from app.retrieval.hybrid import HybridSearchService, reciprocal_rank_fusion
from app.retrieval.qdrant import get_qdrant_manager
from app.retrieval.reranker import DeterministicBaselineRanker
from app.schemas.resource import ResourcePayload


@pytest.mark.asyncio
async def test_qdrant_in_memory_crud_and_search():
    qdrant = get_qdrant_manager()
    emb_svc = get_embedding_service()

    payload = ResourcePayload(
        resource_id="res_qdrant_test_1",
        source="test",
        title="PyTorch Deep Learning Tensors",
        description="Working with PyTorch tensor arithmetic and GPU acceleration.",
        skills=["PyTorch", "Deep Learning"],
        topics=["Tensors"],
        difficulty="intermediate",
        quality_score=0.92,
    )
    vec = await emb_svc.embed_query(payload.title)
    count = await qdrant.upsert_resources([payload], [vec])
    assert count == 1

    # Search
    hits = await qdrant.search_vectors(vec, top_k=2)
    assert len(hits) >= 1
    assert hits[0]["payload"]["resource_id"] == "res_qdrant_test_1"


def test_reciprocal_rank_fusion():
    list_1 = [{"id": "doc_a"}, {"id": "doc_b"}, {"id": "doc_c"}]
    list_2 = [{"id": "doc_b"}, {"id": "doc_a"}, {"id": "doc_d"}]
    fused = reciprocal_rank_fusion([list_1, list_2], k=60)
    # doc_a and doc_b appear in both, should rank above doc_c and doc_d
    top_ids = [item["id"] for item in fused[:2]]
    assert "doc_a" in top_ids
    assert "doc_b" in top_ids


@pytest.mark.asyncio
async def test_deterministic_ranker():
    ranker = DeterministicBaselineRanker()
    candidates = [
        {
            "resource_id": "res_1",
            "title": "Deep Learning Course",
            "skills": ["Deep Learning"],
            "difficulty": "intermediate",
            "quality_score": 0.90,
            "prerequisites": ["Python"],
        },
        {
            "resource_id": "res_2",
            "title": "Beginner Scratch Coding",
            "skills": ["Scratch"],
            "difficulty": "beginner",
            "quality_score": 0.70,
            "prerequisites": [],
        },
    ]
    ranked = await ranker.rank(
        query="Deep Learning",
        candidates=candidates,
        learner_context={"experience_level": "intermediate"},
        verified_skills={"Python": 0.85},
        skill_gaps=[{"skill": "Deep Learning", "gap_magnitude": 0.5}],
    )
    assert len(ranked) == 2
    assert ranked[0].resource_id == "res_1"
    assert ranked[0].score > ranked[1].score
