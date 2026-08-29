"""
Skill Analysis Workflow State.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from app.schemas.skill import SkillAnalysisData, SkillGap


class SkillAnalysisWorkflowState(BaseModel):
    request_id: str
    learner_profile: Dict[str, Any] = Field(default_factory=dict)
    assessment_results: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(default_factory=list)
    verified_skills_input: List[Dict[str, Any]] = Field(default_factory=list)
    self_reported_skills: Dict[str, Any] = Field(default_factory=dict)
    learning_history: List[Dict[str, Any]] = Field(default_factory=list)
    goal: Optional[Union[str, Dict[str, Any]]] = None
    target_skills: List[str] = Field(default_factory=list)

    # Output / progression fields
    verified_scores: Dict[str, float] = Field(default_factory=dict)
    combined_skills: Dict[str, float] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    skill_gaps: List[SkillGap] = Field(default_factory=list)
    final_output: Optional[SkillAnalysisData] = None
    errors: List[str] = Field(default_factory=list)
    status: str = "initialized"
