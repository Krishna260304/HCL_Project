"""
Goal Analysis Workflow State.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.goal import GoalAnalysisData


class GoalAnalysisWorkflowState(BaseModel):
    request_id: str
    user_id: Optional[str] = None
    goal: str
    learner_profile: Dict[str, Any] = Field(default_factory=dict)
    knowledge_areas: List[str] = Field(default_factory=list)
    experience_level: str = "intermediate"
    learning_history: List[Dict[str, Any]] = Field(default_factory=list)
    target_outcome: Optional[str] = None
    timeline: Optional[str] = None

    # Intermediate / Output fields
    normalized_goal: Optional[str] = None
    required_domains: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    possible_roles: List[str] = Field(default_factory=list)
    final_output: Optional[GoalAnalysisData] = None
    errors: List[str] = Field(default_factory=list)
    status: str = "initialized"
