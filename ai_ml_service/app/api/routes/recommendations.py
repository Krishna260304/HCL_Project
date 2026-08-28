"""
Recommendation API Route.
"""

from fastapi import APIRouter, Depends
from app.core.security import verify_api_key
from app.schemas.common import BaseResponse
from app.schemas.recommendation import RecommendationData, RecommendationRequest
from app.services.recommendation_service import RecommendationService, get_recommendation_service
from app.utils.ids import generate_request_id

router = APIRouter(tags=["Recommendations"])


@router.post("/recommendations/generate", response_model=BaseResponse[RecommendationData])
@router.post("/recommendation", response_model=BaseResponse[RecommendationData])
async def generate_recommendations(
    request: RecommendationRequest,
    authenticated: bool = Depends(verify_api_key),
    service: RecommendationService = Depends(get_recommendation_service),
) -> BaseResponse[RecommendationData]:
    """Generate multi-factor hybrid recommendations with evidence-grounded explanations."""
    req_id = request.request_id or generate_request_id()
    request.request_id = req_id
    result = await service.generate(request)
    return BaseResponse(
        success=True,
        request_id=req_id,
        data=result,
        metadata={"recommendations_count": len(result.recommendations), "workflow": "recommendation_graph"},
    )
