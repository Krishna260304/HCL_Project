"""
AI Learning Assistant Request, Context, and Response Schemas.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.rag import RAGSource


class AssistantContext(BaseModel):
    current_goal: Optional[str] = None
    current_phase: Optional[str] = None
    current_topic: Optional[str] = None
    verified_skills: Dict[str, float] = Field(default_factory=dict)
    skill_gaps: List[str] = Field(default_factory=list)
    progress_percentage: float = 0.0
    recent_assessment_score: Optional[float] = None
    recommended_resources: List[str] = Field(default_factory=list)


class AssistantChatRequest(BaseModel):
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    user_id: Optional[str] = Field(None)
    conversation_id: Optional[str] = Field(None)
    message: str = Field(..., min_length=1)
    learner_context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    history: Optional[List[Dict[str, str]]] = Field(default_factory=list)


class AssistantChatData(BaseModel):
    reply: str
    sources: List[RAGSource] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    tools_executed: List[str] = Field(default_factory=list)
    context_used: Dict[str, Any] = Field(default_factory=dict)
