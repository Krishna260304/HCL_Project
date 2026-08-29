"""
Recommendation Workflow State.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from app.schemas.recommendation import RecommendationData, RecommendationItem


class RecommendationWorkflowState(BaseModel):
    request_id: str
    user_id: Optional[str] = None
    learner_profile: Dict[str, Any] = Field(default_factory=dict)
    verified_skills: Dict[str, float] = Field(default_factory=dict)
    skill_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    goal: Optional[Union[str, Dict[str, Any]]] = None
    candidate_resources: List[Dict[str, Any]] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    learning_history: List[Dict[str, Any]] = Field(default_factory=list)
    limit: int = 10

    # Intermediate artifacts
    retrieved_candidates: List[Dict[str, Any]] = Field(default_factory=list)
    ranked_items: List[RecommendationItem] = Field(default_factory=list)
    final_output: Optional[RecommendationData] = None
    errors: List[str] = Field(default_factory=list)
    status: str = "initialized"
