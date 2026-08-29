"""
AI Learning Assistant Service with Context & Streaming Support.
"""

from typing import Any, AsyncIterator, Dict, Optional
from app.llm.generation import get_generation_service
from app.schemas.assistant import AssistantChatData, AssistantChatRequest
from app.schemas.rag import RAGQueryRequest
from app.services.rag_service import get_rag_service


class AssistantService:
    def __init__(self):
        self.rag_service = get_rag_service()
        self.generation_service = get_generation_service()

    async def chat(self, request: AssistantChatRequest) -> AssistantChatData:
        """Process conversational query with learner context and tool execution."""
        rag_req = RAGQueryRequest(
            request_id=request.request_id,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            query=request.message,
            learner_context=request.learner_context or {},
        )
        rag_data = await self.rag_service.query(rag_req)

        tools_executed = ["search_resources", "get_learner_context"]
        return AssistantChatData(
            reply=rag_data.answer,
            sources=rag_data.sources,
            suggested_actions=rag_data.recommended_actions,
            tools_executed=tools_executed,
            context_used=request.learner_context or {},
        )

    async def stream_chat(self, request: AssistantChatRequest) -> AsyncIterator[str]:
        """Stream conversational tutor response tokens."""
        prompt_vars = {
            "context": request.learner_context or {},
            "history": request.history or [],
            "message": request.message,
        }
        async for chunk in self.generation_service.stream_text(
            prompt_name="assistant_v1",
            prompt_vars=prompt_vars,
            system_prompt="You are the LearnPath AI Assistant. Guide the learner through their curriculum with encouraging, context-aware pedagogical advice.",
        ):
            yield chunk


_assistant_service: Optional[AssistantService] = None


def get_assistant_service() -> AssistantService:
    global _assistant_service
    if _assistant_service is None:
        _assistant_service = AssistantService()
    return _assistant_service
