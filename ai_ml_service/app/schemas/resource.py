"""
Resource Analysis, Ingestion, and Payload Schemas.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResourcePayload(BaseModel):
    resource_id: str = Field(..., description="Unique resource identifier")
    source: str = Field("custom", description="youtube, coursera, github, article, documentation, etc.")
    title: str = Field(..., description="Resource title")
    description: Optional[str] = Field(None, description="Resource text description")
    skills: List[str] = Field(default_factory=list, description="Associated skills")
    topics: List[str] = Field(default_factory=list, description="Specific topics covered")
    difficulty: str = Field("intermediate", description="beginner, intermediate, advanced")
    resource_type: str = Field("article", description="course, video, playlist, article, documentation, project, exercise, lab, quiz")
    duration_minutes: int = Field(30, ge=1, description="Estimated duration in minutes")
    language: str = Field("en", description="Language code")
    url: Optional[str] = Field(None, description="Source URL")
    quality_score: float = Field(0.85, ge=0.0, le=1.0, description="Heuristic or verified quality score")
    prerequisites: List[str] = Field(default_factory=list, description="Prerequisite skills")


class ResourceAnalysisRequest(BaseModel):
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    title: str = Field(..., description="Resource title")
    description: Optional[str] = Field("", description="Resource text content or description")
    source: Optional[str] = Field("web", description="Origin source platform")
    url: Optional[str] = Field(None, description="Resource URL")
    skills: Optional[List[str]] = Field(default_factory=list)
    difficulty: Optional[str] = Field(None)
    duration: Optional[int] = Field(None)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ResourceAnalysisData(BaseModel):
    skills: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    difficulty: str = Field("beginner")
    prerequisites: List[str] = Field(default_factory=list)
    quality_score: float = Field(0.85, ge=0.0, le=1.0)
    estimated_duration: int = Field(30)
    learning_format: str = Field("article")
    quality_signals: Dict[str, Any] = Field(default_factory=dict)
    summary: str = Field("")
    semantic_text: str = Field("")
    confidence: float = Field(0.9, ge=0.0, le=1.0)


class ResourceBatchIngestRequest(BaseModel):
    request_id: Optional[str] = Field(None)
    resources: List[ResourcePayload] = Field(..., min_length=1)


class ResourceIngestResponse(BaseModel):
    ingested_count: int
    failed_count: int = 0
    collection: str
    errors: List[str] = Field(default_factory=list)
