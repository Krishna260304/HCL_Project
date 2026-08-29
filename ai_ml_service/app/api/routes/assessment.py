"""
Assessment Generation API Route.
"""

from fastapi import APIRouter, Depends
from app.core.security import verify_api_key
from app.schemas.assessment import AssessmentData, AssessmentGenerationRequest
from app.schemas.common import BaseResponse
from app.services.assessment_service import AssessmentService, get_assessment_service
from app.utils.ids import generate_request_id

router = APIRouter(tags=["Assessment Generation"])


@router.post("/assessment/generate", response_model=BaseResponse[AssessmentData])
@router.post("/assessment-generation", response_model=BaseResponse[AssessmentData])
async def generate_assessment(
    request: AssessmentGenerationRequest,
    authenticated: bool = Depends(verify_api_key),
    service: AssessmentService = Depends(get_assessment_service),
) -> BaseResponse[AssessmentData]:
    """Generate diagnostic MCQ assessment with deterministic psychometric validation."""
    req_id = request.request_id or generate_request_id()
    request.request_id = req_id
    result = await service.generate(request)
    return BaseResponse(
        success=True,
        request_id=req_id,
        data=result,
        metadata={"questions_count": len(result.questions), "workflow": "assessment_graph"},
    )
