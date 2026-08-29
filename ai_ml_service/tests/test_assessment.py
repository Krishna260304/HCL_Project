"""
Tests for Assessment Generation and Question Validation.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_assessment_generation(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "request_id": "test_asm_001",
        "goal": "Machine Learning",
        "experience_level": "intermediate",
        "knowledge_areas": ["Python", "Deep Learning", "Machine Learning"],
        "num_questions": 3,
    }
    response = await async_client.post("/v1/assessment/generate", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert "questions" in data
    assert len(data["questions"]) > 0

    # Validate question structure
    for q in data["questions"]:
        assert len(q["options"]) >= 2
        assert q["correct_answer"] in q["options"]
        assert len(q["learning_objective"]) > 0
        assert len(q["explanation"]) > 0


@pytest.mark.asyncio
async def test_assessment_legacy_alias(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "goal": "Data Science",
        "experience_level": "beginner",
        "skills": ["Python", "Pandas"],
    }
    response = await async_client.post("/assessment-generation", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
