"""
Tests for API Key Security and Unauthorized Rejection.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_unauthorized_request_rejected(async_client: AsyncClient):
    # Attempting to call protected endpoint without Bearer token
    response = await async_client.post(
        "/v1/goal/analyze",
        json={"goal": "Machine Learning Engineer"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_authorized_request_accepted(async_client: AsyncClient, auth_headers: dict):
    response = await async_client.post(
        "/v1/goal/analyze",
        json={"goal": "Machine Learning Engineer"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["goal"] == "Machine Learning Engineer"
