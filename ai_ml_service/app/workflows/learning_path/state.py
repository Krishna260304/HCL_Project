"""
Learning Path Workflow State.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from app.schemas.learning_path import LearningPathData, LearningPhase


class LearningPathWorkflowState(BaseModel):
    request_id: str
    user_id: Optional[str] = None
    goal: Optional[Union[str, Dict[str, Any]]] = None
    verified_skills: Dict[str, float] = Field(default_factory=dict)
    skill_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    skill_graph: Dict[str, Any] = Field(default_factory=dict)
    candidate_resources: List[Dict[str, Any]] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    experience_level: str = "intermediate"
    timeline: str = "8 weeks"

    # Progression artifacts
    phases: List[LearningPhase] = Field(default_factory=list)
    is_valid: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    final_output: Optional[LearningPathData] = None
    errors: List[str] = Field(default_factory=list)
    status: str = "initialized"
