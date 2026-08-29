"""
Learning Path Generation API Route.
"""

from fastapi import APIRouter, Depends
from app.core.security import verify_api_key
from app.schemas.common import BaseResponse
from app.schemas.learning_path import LearningPathData, LearningPathRequest
from app.services.learning_path_service import LearningPathService, get_learning_path_service
from app.utils.ids import generate_request_id

router = APIRouter(tags=["Learning Path"])


@router.post("/learning-path/generate", response_model=BaseResponse[LearningPathData])
@router.post("/learning-path", response_model=BaseResponse[LearningPathData])
async def generate_learning_path(
    request: LearningPathRequest,
    authenticated: bool = Depends(verify_api_key),
    service: LearningPathService = Depends(get_learning_path_service),
) -> BaseResponse[LearningPathData]:
    """Generate structured, multi-phase DAG-validated personalized learning path."""
    req_id = request.request_id or generate_request_id()
    request.request_id = req_id
    result = await service.generate(request)
    return BaseResponse(
        success=True,
        request_id=req_id,
        data=result,
        metadata={"phases_count": len(result.phases), "workflow": "learning_path_graph"},
    )
