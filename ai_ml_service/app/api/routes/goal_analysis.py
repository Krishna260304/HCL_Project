"""
Goal Analysis API Route.
"""

from fastapi import APIRouter, Depends
from app.core.security import verify_api_key
from app.schemas.common import BaseResponse
from app.schemas.goal import GoalAnalysisData, GoalAnalysisRequest
from app.services.goal_service import GoalService, get_goal_service
from app.utils.ids import generate_request_id

router = APIRouter(tags=["Goal Analysis"])


@router.post("/goal/analyze", response_model=BaseResponse[GoalAnalysisData])
@router.post("/goal-analysis", response_model=BaseResponse[GoalAnalysisData])
async def analyze_goal(
    request: GoalAnalysisRequest,
    authenticated: bool = Depends(verify_api_key),
    service: GoalService = Depends(get_goal_service),
) -> BaseResponse[GoalAnalysisData]:
    """Analyze learner goal text and extract structured domains, skills, and timeline."""
    req_id = request.request_id or generate_request_id()
    request.request_id = req_id
    result = await service.analyze(request)
    return BaseResponse(
        success=True,
        request_id=req_id,
        data=result,
        metadata={"workflow": "goal_analysis_graph"},
    )
