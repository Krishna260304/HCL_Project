"""
Assessment Generation Workflow State.
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from app.schemas.assessment import AssessmentBlueprint, AssessmentData, MCQQuestion


class AssessmentWorkflowState(BaseModel):
    request_id: str
    goal: str
    experience_level: str = "intermediate"
    knowledge_areas: List[str] = Field(default_factory=list)
    self_reported_skills: Dict[str, Any] = Field(default_factory=dict)
    learning_history: List[Dict[str, Any]] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    num_questions: int = 5

    # Graph progression artifacts
    blueprint: Optional[AssessmentBlueprint] = None
    generated_questions: List[MCQQuestion] = Field(default_factory=list)
    valid_questions: List[MCQQuestion] = Field(default_factory=list)
    invalid_questions: List[Tuple[int, MCQQuestion, str]] = Field(default_factory=list)
    repair_attempts: int = 0
    final_output: Optional[AssessmentData] = None
    errors: List[str] = Field(default_factory=list)
    status: str = "initialized"
