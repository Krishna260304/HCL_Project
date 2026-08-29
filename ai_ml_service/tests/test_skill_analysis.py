"""
Tests for Skill Analysis and Gap Estimation.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_skill_analysis_differentiates_verified_from_self_reported(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "request_id": "test_sk_001",
        "verified_skills": [
            {"skill_id": "Python", "verified_score": 0.91},
            {"skill_id": "Deep Learning", "verified_score": 0.43},
        ],
        "self_reported_skills": {
            "MLOps": "beginner",
            "Statistics": "advanced",
        },
        "target_skills": ["Python", "Deep Learning", "MLOps"],
    }
    response = await async_client.post("/v1/skills/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]

    # Verify scores are preserved and not overwritten
    assert data["verified_scores"]["Python"] == 0.91
    assert data["verified_scores"]["Deep Learning"] == 0.43
    assert "MLOps" in data["skills"]
    assert len(data["skill_gaps"]) > 0


@pytest.mark.asyncio
async def test_skill_analysis_legacy_alias(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "verified_skills": [{"skill_id": "Python", "verified_score": 85}],
    }
    response = await async_client.post("/skill-analysis", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
