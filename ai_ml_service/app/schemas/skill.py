"""
Skill Analysis and Estimation Schemas.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class SkillScore(BaseModel):
    skill: str
    verified_score: float = Field(..., ge=0.0, le=1.0, description="Score validated through assessment (0.0 - 1.0)")
    self_reported_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Subjective score (0.0 - 1.0)")
    confidence: float = Field(0.85, ge=0.0, le=1.0)
    level: str = Field("intermediate", description="beginner, intermediate, advanced, expert")


class SkillGap(BaseModel):
    skill: str
    current_score: float = Field(..., ge=0.0, le=1.0)
    target_score: float = Field(..., ge=0.0, le=1.0)
    gap_magnitude: float = Field(..., ge=0.0, le=1.0)
    priority: str = Field("high", description="high, medium, low")


class SkillAnalysisRequest(BaseModel):
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    learner_profile: Optional[Dict[str, Any]] = Field(default_factory=dict)
    assessment_results: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = Field(default_factory=list)
    verified_skills: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    self_reported_skills: Optional[Dict[str, Any]] = Field(default_factory=dict)
    learning_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    goal: Optional[Union[str, Dict[str, Any]]] = None
    target_skills: Optional[List[str]] = Field(default_factory=list)


class SkillAnalysisData(BaseModel):
    skills: Dict[str, float] = Field(default_factory=dict, description="Skill to score map (0.0 to 1.0)")
    verified_scores: Dict[str, float] = Field(default_factory=dict, description="Verified assessment scores")
    estimated_skill_levels: Dict[str, float] = Field(default_factory=dict, description="Estimated skill levels (0-100 or 0-1)")
    strengths: List[str] = Field(default_factory=list, description="Validated strong skills")
    weaknesses: List[str] = Field(default_factory=list, description="Identified weak skills")
    skill_gaps: List[SkillGap] = Field(default_factory=list, description="Gaps between current and target")
    recommended_next_skills: List[str] = Field(default_factory=list, description="Recommended immediate learning focus")
    confidence: float = Field(0.9, ge=0.0, le=1.0)
