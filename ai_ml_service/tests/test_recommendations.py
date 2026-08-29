"""
Tests for Recommendation Generation and Grounded Explanations.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_recommendations_generation(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "request_id": "test_rec_001",
        "goal": "Machine Learning Engineer",
        "verified_skills": {"Python": 0.90, "Machine Learning": 0.80},
        "skill_gaps": [{"skill": "Deep Learning", "gap_magnitude": 0.40}],
        "candidate_resources": [
            {
                "resource_id": "res_dl_01",
                "title": "Deep Learning PyTorch Bootcamp",
                "skills": ["Deep Learning", "PyTorch"],
                "difficulty": "intermediate",
                "quality_score": 0.95,
                "prerequisites": ["Python"],
            },
            {
                "resource_id": "res_web_01",
                "title": "HTML and CSS Fundamentals",
                "skills": ["HTML", "CSS"],
                "difficulty": "beginner",
                "quality_score": 0.80,
                "prerequisites": [],
            },
        ],
    }
    response = await async_client.post("/v1/recommendations/generate", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert "recommendations" in data
    assert len(data["recommendations"]) > 0

    # Deep learning resource should rank higher due to skill gap match
    top_item = data["recommendations"][0]
    assert top_item["resource_id"] == "res_dl_01"
    assert "reason" in top_item
    assert top_item["score"] > 0.0
