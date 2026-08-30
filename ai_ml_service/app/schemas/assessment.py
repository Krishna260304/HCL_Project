"""
Assessment Generation Request and MCQ Schemas.
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class MCQQuestion(BaseModel):
    id: Optional[str] = Field(None, description="Unique question identifier")
    question: str = Field(..., min_length=5, description="Question stem text")
    options: List[str] = Field(..., min_length=2, description="Multiple choice options")
    correct_answer: str = Field(..., description="Exact string matching one of the options")
    skill: Optional[str] = Field(None, description="Target skill evaluated")
    skill_id: Optional[str] = Field(None, description="Target skill identifier (alias)")
    topic: str = Field(..., description="Specific topic within skill")
    difficulty: str = Field("intermediate", description="beginner, intermediate, advanced")
    learning_objective: str = Field(..., description="Learning outcome evaluated by question")
    explanation: str = Field(..., description="Explanation of why the correct answer is right")

    def get_skill(self) -> str:
        return self.skill or self.skill_id or "General"


class AssessmentBlueprint(BaseModel):
    title: str = "Diagnostic Assessment"
    description: str = "Adaptive diagnostic assessment tailored to your background"
    target_skills: List[str] = Field(default_factory=list)
    difficulty_distribution: Dict[str, int] = Field(default_factory=lambda: {"beginner": 1, "intermediate": 3, "advanced": 1})
    total_questions: int = 5


class AssessmentGenerationRequest(BaseModel):
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    goal: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Learner goal title or object")
    experience_level: Optional[str] = Field("intermediate", description="beginner, intermediate, advanced")
    knowledge_areas: Optional[List[str]] = Field(default_factory=list, description="Knowledge areas to assess")
    skills: Optional[List[str]] = Field(default_factory=list, description="Explicit skills to target")
    self_reported_skills: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Self reported skill levels")
    learning_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Past courses/assessments")
    required_skills: Optional[List[str]] = Field(default_factory=list, description="Required target skills")
    num_questions: Optional[int] = Field(5, ge=5, le=10, description="Desired number of questions (5 to 10)")


class AssessmentData(BaseModel):
    title: str = Field(..., description="Assessment title")
    description: str = Field(..., description="Assessment description")
    difficulty: str = Field("intermediate", description="Overall difficulty")
    duration: int = Field(20, description="Estimated duration in minutes")
    skill_ids: List[str] = Field(default_factory=list, description="Skills assessed")
    topic_ids: List[str] = Field(default_factory=list, description="Topics assessed")
    questions: List[MCQQuestion] = Field(default_factory=list, description="Generated validated questions")
    confidence: float = Field(0.9, ge=0.0, le=1.0)
