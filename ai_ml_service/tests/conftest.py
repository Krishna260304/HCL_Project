"""
Pytest configuration and shared fixtures for AI/ML Service tests.
"""

import os
import sys
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Enforce mock mode and test api key for unit tests
os.environ["AI_MOCK_MODE"] = "true"
os.environ["AI_SERVICE_API_KEY"] = "test-secret-key"
os.environ["EMBEDDING_PROVIDER"] = "mock"
os.environ["LLM_PROVIDER"] = "mock"

from app.core.config import get_settings
from app.main import app

get_settings.cache_clear()


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-secret-key"}


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
