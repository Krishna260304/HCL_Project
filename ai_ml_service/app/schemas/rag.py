"""
RAG (Retrieval-Augmented Generation) Schemas.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RAGSource(BaseModel):
    title: str
    url: Optional[str] = None
    source_type: str = "documentation"
    snippet: str = ""
    relevance_score: float = 0.85
    resource_id: Optional[str] = None


class RAGQueryRequest(BaseModel):
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    user_id: Optional[str] = Field(None)
    conversation_id: Optional[str] = Field(None)
    query: Optional[str] = Field(None, description="Learner search / query text")
    message: Optional[str] = Field(None, description="Alternative message parameter")
    learner_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    top_k: Optional[int] = Field(5, ge=1, le=20)

    def get_query_text(self) -> str:
        return (self.query or self.message or "").strip()


class RAGQueryData(BaseModel):
    answer: str = Field(..., description="Grounded natural language response")
    sources: List[RAGSource] = Field(default_factory=list, description="Explicit retrieved source citations")
    recommended_actions: List[str] = Field(default_factory=list, description="Actionable next steps")
    context_metadata: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(0.9, ge=0.0, le=1.0)
