"""
Common Response, Error, and Metadata schemas.
Standardizes all API outputs across the AI/ML Service.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional context or validation details")


class ErrorResponse(BaseModel):
    success: bool = Field(default=False, description="Always false for error responses")
    request_id: str = Field(..., description="Unique request correlation ID")
    error: ErrorDetail = Field(..., description="Error detail payload")


class BaseResponse(BaseModel, Generic[DataT]):
    success: bool = Field(default=True, description="Indicates if the request succeeded")
    request_id: str = Field(..., description="Unique request correlation ID")
    data: DataT = Field(..., description="Domain-specific response payload")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Execution metadata (timing, model, tokens)")


class GPUDiagnostics(BaseModel):
    cuda_available: bool
    gpu_count: int
    gpu_name: str
    vram_gb: float
    torch_cuda_version: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "learnpath-ai-ml"
    version: str = "1.0.0"
    llm: str = "ready"
    embeddings: str = "ready"
    qdrant: str = "ready"
    mock_mode: bool = False
    gpu: GPUDiagnostics


class JobStatusResponse(BaseModel):
    job_id: str
    status: str = Field(..., description="queued, running, completed, failed")
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    result: Optional[Dict[str, Any]] = None
    error: Optional[ErrorDetail] = None
