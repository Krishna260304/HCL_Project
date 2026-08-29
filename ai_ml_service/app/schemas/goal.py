"""
Goal Analysis Request and Response Schemas.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GoalAnalysisRequest(BaseModel):
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    user_id: Optional[str] = Field(None, description="Learner unique identifier")
    goal: Optional[str] = Field(None, description="Primary goal string")
    description: Optional[str] = Field(None, description="Alternative goal text / description")
    learner_profile: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Learner background profile")
    knowledge_areas: Optional[List[str]] = Field(default_factory=list, description="Self-reported knowledge domains")
    experience_level: Optional[str] = Field("beginner", description="beginner, intermediate, advanced")
    learning_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Past courses or activities")
    target_outcome: Optional[str] = Field(None, description="Target career role or academic outcome")
    timeline: Optional[str] = Field(None, description="Preferred duration or timeline")

    def get_goal_text(self) -> str:
        return (self.goal or self.description or "General Technology Skills").strip()


class GoalAnalysisData(BaseModel):
    goal: str = Field(..., description="Normalized goal title")
    goal_type: str = Field(..., description="career_transition, skill_advancement, project_mastery, general_learning")
    target_outcome: str = Field(..., description="Target outcome description")
    timeline: str = Field(..., description="Estimated completion timeline")
    required_domains: List[str] = Field(default_factory=list, description="Key domain areas required")
    recommended_domains: List[str] = Field(default_factory=list, description="Recommended domains for compatibility")
    required_skills: List[str] = Field(default_factory=list, description="Specific skills needed")
    possible_roles: List[str] = Field(default_factory=list, description="Potential job or skill titles")
    confidence: float = Field(0.9, ge=0.0, le=1.0, description="Model confidence score")
