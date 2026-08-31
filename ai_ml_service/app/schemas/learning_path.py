"""
Learning Path Generation and Validation Schemas.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class PhaseResource(BaseModel):
    resource_id: str = "res_01"
    title: str = "Core Concept Guide"
    resource_type: str = Field("documentation", description="video, article, course, documentation, exercise, lab")
    url: Optional[str] = None
    duration_minutes: int = 45
    skills: List[str] = Field(default_factory=list)
    is_mandatory: bool = True


class PhaseProject(BaseModel):
    project_id: str = "proj_01"
    title: str = "Applied Milestone Project"
    description: str = "Practical hands-on implementation reinforcing phase objectives."
    difficulty: str = "intermediate"
    estimated_hours: int = 6
    deliverables: List[str] = Field(default_factory=lambda: ["Source Code", "Documentation"])


class PhaseAssessment(BaseModel):
    assessment_id: Optional[str] = "asm_01"
    title: str = "Milestone Diagnostic Evaluation"
    type: str = "milestone_quiz"
    pass_score: float = 0.70


class LearningPhase(BaseModel):
    phase_id: str = "phase_1"
    title: str = "Phase 1: Core Foundations"
    description: str = "Foundational concepts and practical applications."
    objective: Optional[str] = "Master core domain principles and practical tooling."
    order: int = 1
    skills: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    resources: List[Union[PhaseResource, Dict[str, Any]]] = Field(default_factory=list)
    projects: List[Union[PhaseProject, Dict[str, Any]]] = Field(default_factory=list)
    assessment: Optional[Union[PhaseAssessment, Dict[str, Any]]] = None
    assessment_id: Optional[str] = None
    milestone: str = "Phase milestone reached"
    estimated_duration_weeks: int = 2
    explanation: Optional[str] = "Core prerequisite progression."


class LearningPathRequest(BaseModel):
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    user_id: Optional[str] = Field(None)
    goal: Optional[Union[str, Dict[str, Any]]] = None
    verified_skills: Optional[Union[Dict[str, float], List[Dict[str, Any]]]] = Field(default_factory=dict)
    skill_gaps: Optional[List[Union[str, Dict[str, Any]]]] = Field(default_factory=list)
    skill_graph: Optional[Dict[str, Any]] = Field(default_factory=dict)
    resources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    candidate_resources: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    constraints: Optional[Dict[str, Any]] = Field(default_factory=dict)
    experience_level: Optional[str] = "intermediate"
    timeline: Optional[str] = "8 weeks"


class LearningPathData(BaseModel):
    title: str
    description: str
    goal: str
    estimated_duration_weeks: int = 8
    target_role: Optional[str] = None
    phases: List[LearningPhase] = Field(default_factory=list)
    validation_status: str = Field("validated", description="validated, requires_admin_review, approved")
    confidence: float = Field(0.92, ge=0.0, le=1.0)
