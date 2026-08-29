"""
Adaptive Learning API Route.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends
from app.core.security import verify_api_key
from app.schemas.common import BaseResponse
from app.services.adaptive_learning_service import (
    AdaptiveLearningService,
    AdaptiveUpdateData,
    get_adaptive_learning_service,
)
from app.utils.ids import generate_request_id

router = APIRouter(tags=["Adaptive Learning"])


@router.post("/adaptive/update", response_model=BaseResponse[AdaptiveUpdateData])
@router.post("/adaptive-learning/evaluate", response_model=BaseResponse[AdaptiveUpdateData])
async def evaluate_adaptation(
    payload: Dict[str, Any],
    authenticated: bool = Depends(verify_api_key),
    service: AdaptiveLearningService = Depends(get_adaptive_learning_service),
) -> BaseResponse[AdaptiveUpdateData]:
    """Evaluate learner performance delta and generate adaptive roadmap modifications."""
    req_id = payload.get("request_id") or generate_request_id()
    payload["request_id"] = req_id
    result = await service.update(payload)
    return BaseResponse(
        success=True,
        request_id=req_id,
        data=result,
        metadata={"workflow": "adaptive_learning_graph"},
    )
