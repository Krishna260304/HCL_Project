"""
RAG Workflow State.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.rag import RAGQueryData, RAGSource


class RAGWorkflowState(BaseModel):
    request_id: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    query: str
    learner_context: Dict[str, Any] = Field(default_factory=dict)
    top_k: int = 5

    # Intermediate retrieval and generation artifacts
    retrieved_documents: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[RAGSource] = Field(default_factory=list)
    final_output: Optional[RAGQueryData] = None
    errors: List[str] = Field(default_factory=list)
    status: str = "initialized"
