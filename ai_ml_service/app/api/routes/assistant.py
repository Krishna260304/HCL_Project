"""
AI Assistant API Routes.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.core.security import verify_api_key
from app.schemas.assistant import AssistantChatData, AssistantChatRequest
from app.schemas.common import BaseResponse
from app.services.assistant_service import AssistantService, get_assistant_service
from app.utils.ids import generate_request_id

router = APIRouter(tags=["AI Learning Assistant"])


@router.post("/assistant/chat", response_model=BaseResponse[AssistantChatData])
async def chat_with_assistant(
    request: AssistantChatRequest,
    authenticated: bool = Depends(verify_api_key),
    service: AssistantService = Depends(get_assistant_service),
) -> BaseResponse[AssistantChatData]:
    """Interactive AI tutor chat with learner context awareness."""
    req_id = request.request_id or generate_request_id()
    request.request_id = req_id
    result = await service.chat(request)
    return BaseResponse(
        success=True,
        request_id=req_id,
        data=result,
        metadata={"tools_executed": result.tools_executed},
    )


@router.post("/assistant/stream")
async def stream_chat_with_assistant(
    request: AssistantChatRequest,
    authenticated: bool = Depends(verify_api_key),
    service: AssistantService = Depends(get_assistant_service),
):
    """Stream AI tutor conversation tokens."""
    return StreamingResponse(
        service.stream_chat(request),
        media_type="text/event-stream",
    )
