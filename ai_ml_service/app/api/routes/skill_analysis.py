"""
Skill Analysis API Route.
"""

from fastapi import APIRouter, Depends
from app.core.security import verify_api_key
from app.schemas.common import BaseResponse
from app.schemas.skill import SkillAnalysisData, SkillAnalysisRequest
from app.services.skill_service import SkillService, get_skill_service
from app.utils.ids import generate_request_id

router = APIRouter(tags=["Skill Analysis"])


@router.post("/skills/analyze", response_model=BaseResponse[SkillAnalysisData])
@router.post("/skill-analysis", response_model=BaseResponse[SkillAnalysisData])
async def analyze_skills(
    request: SkillAnalysisRequest,
    authenticated: bool = Depends(verify_api_key),
    service: SkillService = Depends(get_skill_service),
) -> BaseResponse[SkillAnalysisData]:
    """Estimate verified skill scores and compute target skill gaps."""
    req_id = request.request_id or generate_request_id()
    request.request_id = req_id
    result = await service.analyze(request)
    return BaseResponse(
        success=True,
        request_id=req_id,
        data=result,
        metadata={"gaps_count": len(result.skill_gaps), "workflow": "skill_analysis_graph"},
    )
