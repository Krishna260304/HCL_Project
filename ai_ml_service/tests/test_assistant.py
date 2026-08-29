"""
Tests for AI Learning Assistant Chat and Context.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_assistant_chat(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "message": "What should I study next in my roadmap?",
        "learner_context": {
            "current_goal": "Machine Learning Engineer",
            "current_phase": "Phase 1: Foundations",
            "progress_percentage": 25.0,
            "skill_gaps": ["Deep Learning"],
        },
    }
    response = await async_client.post("/v1/assistant/chat", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert "reply" in data
    assert len(data["reply"]) > 0
    assert "suggested_actions" in data
    assert "tools_executed" in data
