"""
Resource Analysis Workflow State.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.resource import ResourceAnalysisData, ResourcePayload


class ResourceAnalysisWorkflowState(BaseModel):
    request_id: str
    title: str
    description: str = ""
    source: str = "web"
    url: Optional[str] = None
    explicit_skills: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Generated attributes
    normalized_payload: Optional[ResourcePayload] = None
    embedding_vector: Optional[List[float]] = None
    final_output: Optional[ResourceAnalysisData] = None
    errors: List[str] = Field(default_factory=list)
    status: str = "initialized"
