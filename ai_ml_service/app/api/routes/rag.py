"""
RAG Query API Route.
"""

from fastapi import APIRouter, Depends
from app.core.security import verify_api_key
from app.schemas.common import BaseResponse
from app.schemas.rag import RAGQueryData, RAGQueryRequest
from app.services.rag_service import RAGService, get_rag_service
from app.utils.ids import generate_request_id

router = APIRouter(tags=["RAG & Knowledge Retrieval"])


@router.post("/rag/query", response_model=BaseResponse[RAGQueryData])
async def query_rag(
    request: RAGQueryRequest,
    authenticated: bool = Depends(verify_api_key),
    service: RAGService = Depends(get_rag_service),
) -> BaseResponse[RAGQueryData]:
    """Execute citation-grounded RAG query against knowledge base."""
    req_id = request.request_id or generate_request_id()
    request.request_id = req_id
    result = await service.query(request)
    return BaseResponse(
        success=True,
        request_id=req_id,
        data=result,
        metadata={"sources_count": len(result.sources), "workflow": "rag_graph"},
    )
