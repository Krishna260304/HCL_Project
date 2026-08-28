"""
RAG (Retrieval-Augmented Generation) Service.
"""

from typing import Optional
from app.schemas.rag import RAGQueryData, RAGQueryRequest
from app.utils.ids import generate_request_id
from app.workflows.rag.graph import build_rag_graph
from app.workflows.rag.state import RAGWorkflowState


class RAGService:
    def __init__(self):
        self.graph = build_rag_graph()

    async def query(self, request: RAGQueryRequest) -> RAGQueryData:
        req_id = request.request_id or generate_request_id()
        initial_state = RAGWorkflowState(
            request_id=req_id,
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            query=request.get_query_text(),
            learner_context=request.learner_context or {},
            top_k=request.top_k or 5,
        )
        final_state = await self.graph.ainvoke(initial_state)
        out = final_state.get("final_output") if isinstance(final_state, dict) else getattr(final_state, "final_output", None)
        if isinstance(out, RAGQueryData):
            return out
        elif isinstance(out, dict):
            return RAGQueryData.model_validate(out)
        raise RuntimeError("RAG workflow did not return valid output.")


_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
