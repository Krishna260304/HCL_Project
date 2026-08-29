"""
Adaptive Learning Workflow State.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from app.schemas.recommendation import RecommendationItem
from app.schemas.skill import SkillGap


class AdaptiveLearningWorkflowState(BaseModel):
    request_id: str
    previous_learning_path: Dict[str, Any] = Field(default_factory=dict)
    latest_assessment: Dict[str, Any] = Field(default_factory=dict)
    current_skill_scores: Dict[str, float] = Field(default_factory=dict)
    progress: Dict[str, Any] = Field(default_factory=dict)
    goal: Optional[Union[str, Dict[str, Any]]] = None

    # Adaptation outputs
    updated_skill_scores: Dict[str, float] = Field(default_factory=dict)
    new_skill_gaps: List[SkillGap] = Field(default_factory=list)
    path_changes: List[Dict[str, Any]] = Field(default_factory=list)
    new_recommendations: List[RecommendationItem] = Field(default_factory=list)
    reason: str = ""
    re_rank_resources: bool = False
    adjust_roadmap: bool = False
    errors: List[str] = Field(default_factory=list)
    status: str = "initialized"
