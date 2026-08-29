"""
Tests for health and GPU diagnostic endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "learnpath-ai-ml"
    assert "gpu" in data
    assert "cuda_available" in data["gpu"]
    assert "vram_gb" in data["gpu"]
