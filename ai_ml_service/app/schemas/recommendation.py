"""
Recommendation Request, Evidence, and Item Schemas.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class RecommendationEvidence(BaseModel):
    skill_gap_match: float = Field(0.0, ge=0.0, le=1.0)
    prerequisite_satisfied: bool = True
    difficulty_aligned: bool = True
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    quality_score: float = Field(0.85, ge=0.0, le=1.0)


class RecommendationItem(BaseModel):
    resource_id: str = Field(..., description="Unique ID of recommended resource")
    title: Optional[str] = Field(None, description="Resource title")
    skill_id: Optional[str] = Field(None, description="Primary skill addressed")
    score: float = Field(..., ge=0.0, le=1.0, description="Overall ranking score")
    reason: str = Field(..., description="Natural language explanation grounded in evidence")
    source: str = Field("hybrid_ranker", description="Origin ranking method")
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    difficulty_match: str = Field("optimal", description="optimal, slightly_hard, too_easy, challenging")
    prerequisite_status: str = Field("satisfied", description="satisfied, missing, partial")
    evidence: Optional[RecommendationEvidence] = None


class RecommendationRequest(BaseModel):
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    user_id: Optional[str] = Field(None)
    learner_profile: Optional[Dict[str, Any]] = Field(default_factory=dict)
    verified_skills: Optional[Union[Dict[str, float], List[Dict[str, Any]]]] = Field(default_factory=dict)
    skill_gaps: Optional[List[Union[str, Dict[str, Any]]]] = Field(default_factory=list)
    goal: Optional[Union[str, Dict[str, Any]]] = None
    resources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    candidate_resources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    constraints: Optional[Dict[str, Any]] = Field(default_factory=dict)
    learning_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    limit: Optional[int] = Field(10, ge=1, le=50)


class RecommendationData(BaseModel):
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
