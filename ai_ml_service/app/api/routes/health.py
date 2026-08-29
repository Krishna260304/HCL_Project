"""
Health and Diagnostic Endpoints.
"""

from fastapi import APIRouter
from app.core.config import get_settings
from app.embeddings.service import get_embedding_service
from app.llm.model import LLMFactory
from app.retrieval.qdrant import get_qdrant_manager
from app.schemas.common import GPUDiagnostics, HealthResponse

router = APIRouter(tags=["Health & Observability"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """System health check and GPU diagnostics."""
    settings = get_settings()
    gpu_diag_dict = settings.get_gpu_diagnostics()
    gpu_diag = GPUDiagnostics(**gpu_diag_dict)

    llm_ready = "ready" if (settings.AI_MOCK_MODE or LLMFactory.get_provider().is_ready()) else "available"
    emb_ready = "ready" if (settings.AI_MOCK_MODE or get_embedding_service().is_ready()) else "available"
    qdrant_ready = "ready" if get_qdrant_manager().is_ready() else "in_memory"

    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version="1.0.0",
        llm=llm_ready,
        embeddings=emb_ready,
        qdrant=qdrant_ready,
        mock_mode=settings.AI_MOCK_MODE,
        gpu=gpu_diag,
    )
