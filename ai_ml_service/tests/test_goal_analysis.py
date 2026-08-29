"""
Tests for Goal Analysis Schema and LangGraph Workflow.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_goal_analysis_v1(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "request_id": "test_goal_001",
        "user_id": "user_123",
        "goal": "I want to become a Machine Learning Engineer",
        "experience_level": "intermediate",
        "knowledge_areas": ["Python", "Linear Algebra"],
        "target_outcome": "Employment as ML Engineer",
        "timeline": "6 months",
    }
    response = await async_client.post("/v1/goal/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert res_json["request_id"] == "test_goal_001"
    data = res_json["data"]
    assert "goal" in data
    assert "required_skills" in data
    assert len(data["required_skills"]) > 0
    assert "timeline" in data


@pytest.mark.asyncio
async def test_goal_analysis_legacy_alias(async_client: AsyncClient, auth_headers: dict):
    # Testing Django compatibility endpoint /goal-analysis
    payload = {"description": "Senior DevOps Engineer"}
    response = await async_client.post("/goal-analysis", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
