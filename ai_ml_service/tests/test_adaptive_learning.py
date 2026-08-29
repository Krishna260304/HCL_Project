"""
Tests for Adaptive Learning Update Workflow.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_adaptive_learning_inserts_remedial_on_low_score(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "request_id": "test_adapt_001",
        "current_skill_scores": {"Deep Learning": 0.70},
        "latest_assessment": {
            "skill": "Deep Learning",
            "score": 0.40,  # low score triggers remediation
        },
    }
    response = await async_client.post("/v1/adaptive/update", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert "updated_skill_scores" in data
    assert data["updated_skill_scores"]["Deep Learning"] < 0.60
    assert len(data["path_changes"]) > 0
    assert data["path_changes"][0]["action"] == "insert_remedial_module"
    assert len(data["new_recommendations"]) > 0


@pytest.mark.asyncio
async def test_adaptive_learning_fast_tracks_on_high_score(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "current_skill_scores": {"Python": 0.60},
        "latest_assessment": {
            "skill": "Python",
            "score": 0.95,  # high score triggers fast-track
        },
    }
    response = await async_client.post("/adaptive-learning/evaluate", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert data["updated_skill_scores"]["Python"] >= 0.80
    assert data["path_changes"][0]["action"] == "mark_competency_mastered"
