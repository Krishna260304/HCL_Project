"""
Tests for Learning Path Generation and Validation.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_learning_path_generation(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "request_id": "test_lp_001",
        "goal": "Machine Learning Engineer",
        "verified_skills": {"Python": 0.85},
        "skill_gaps": ["Deep Learning", "MLOps"],
        "timeline": "8 weeks",
    }
    response = await async_client.post("/v1/learning-path/generate", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert "phases" in data
    assert len(data["phases"]) >= 2

    # Check phase sequencing
    orders = [p["order"] for p in data["phases"]]
    assert orders == list(range(1, len(data["phases"]) + 1))


@pytest.mark.asyncio
async def test_learning_path_legacy_alias(async_client: AsyncClient, auth_headers: dict):
    payload = {"goal": "Full Stack Engineer"}
    response = await async_client.post("/learning-path", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
