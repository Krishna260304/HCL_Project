"""
Tests for Resource Analysis and Batch Ingestion.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_resource_analysis(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "title": "Introduction to Neural Networks in PyTorch",
        "description": "Learn autograd, backpropagation, and basic CNN architectures.",
        "source": "youtube",
        "url": "https://youtube.com/watch?v=sample",
    }
    response = await async_client.post("/v1/resources/analyze", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    data = res_json["data"]
    assert "skills" in data
    assert "difficulty" in data
    assert "prerequisites" in data


@pytest.mark.asyncio
async def test_resource_batch_ingest(async_client: AsyncClient, auth_headers: dict):
    payload = {
        "resources": [
            {
                "resource_id": "test_res_101",
                "source": "article",
                "title": "Attention Is All You Need Paper Walkthrough",
                "description": "Transformers and self-attention mechanism breakdown.",
                "skills": ["Deep Learning", "Transformers", "NLP"],
                "topics": ["Self-Attention", "Multi-Head Attention"],
                "difficulty": "advanced",
                "resource_type": "article",
                "duration_minutes": 45,
                "language": "en",
                "quality_score": 0.95,
                "prerequisites": ["Deep Learning"],
            }
        ]
    }
    response = await async_client.post("/v1/resources/batch-ingest", json=payload, headers=auth_headers)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is True
    assert res_json["data"]["ingested_count"] >= 1
