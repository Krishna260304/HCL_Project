"""
Tests for RAG Query and Citation Grounding.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_rag_query(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "request_id": "test_rag_001",
        "query": "Can I skip linear algebra for machine learning?",
        "learner_context": {
            "current_goal": "Machine Learning Engineer",
            "verified_skills": {"Python": 0.9},
        },
    }
    response = await async_client.post("/v1/rag/query", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert "answer" in data
    assert len(data["answer"]) > 0
    assert "sources" in data
    assert "recommended_actions" in data
