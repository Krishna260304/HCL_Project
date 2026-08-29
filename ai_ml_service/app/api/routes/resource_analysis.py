"""
Resource Analysis and Ingestion API Routes.
"""

from fastapi import APIRouter, Depends
from app.core.security import verify_api_key
from app.schemas.common import BaseResponse
from app.schemas.resource import (
    ResourceAnalysisData,
    ResourceAnalysisRequest,
    ResourceBatchIngestRequest,
    ResourceIngestResponse,
)
from app.services.resource_service import ResourceService, get_resource_service
from app.utils.ids import generate_request_id

router = APIRouter(tags=["Resource Analysis & Ingestion"])


@router.post("/resources/analyze", response_model=BaseResponse[ResourceAnalysisData])
@router.post("/resource-analysis", response_model=BaseResponse[ResourceAnalysisData])
async def analyze_resource(
    request: ResourceAnalysisRequest,
    authenticated: bool = Depends(verify_api_key),
    service: ResourceService = Depends(get_resource_service),
) -> BaseResponse[ResourceAnalysisData]:
    """Extract skills, difficulty, prerequisites, and quality signals from educational resources."""
    req_id = request.request_id or generate_request_id()
    request.request_id = req_id
    result = await service.analyze(request)
    return BaseResponse(
        success=True,
        request_id=req_id,
        data=result,
        metadata={"workflow": "resource_analysis_graph"},
    )


@router.post("/resources/batch-ingest", response_model=BaseResponse[ResourceIngestResponse])
async def batch_ingest_resources(
    request: ResourceBatchIngestRequest,
    authenticated: bool = Depends(verify_api_key),
    service: ResourceService = Depends(get_resource_service),
) -> BaseResponse[ResourceIngestResponse]:
    """Batch embed and index external learning resources into Qdrant vector database."""
    req_id = request.request_id or generate_request_id()
    result = await service.batch_ingest(request)
    return BaseResponse(
        success=True,
        request_id=req_id,
        data=result,
        metadata={"batch_size": len(request.resources)},
    )
