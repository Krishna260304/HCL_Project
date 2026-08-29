"""
Custom Exception Hierarchy for LearnPath AI AI/ML Service.
Maps domain errors to structured error response codes.
"""

from typing import Any, Dict, Optional


class AIServiceException(Exception):
    """Base exception for all AI/ML Service errors."""
    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        if details:
            self.details = details
        else:
            self.details = {}
        if status_code:
            self.status_code = status_code


class InvalidInputError(AIServiceException):
    code = "INVALID_INPUT"
    status_code = 400


class ValidationError(AIServiceException):
    code = "VALIDATION_ERROR"
    status_code = 422


class ModelInferenceError(AIServiceException):
    code = "INFERENCE_ERROR"
    status_code = 500


class ModelUnavailableError(AIServiceException):
    code = "MODEL_ERROR"
    status_code = 503


class RetrievalError(AIServiceException):
    code = "RETRIEVAL_ERROR"
    status_code = 502


class TimeoutError(AIServiceException):
    code = "TIMEOUT"
    status_code = 504


class RateLimitedError(AIServiceException):
    code = "RATE_LIMITED"
    status_code = 429


class AuthenticationError(AIServiceException):
    code = "UNAUTHORIZED"
    status_code = 401


class InsufficientContextError(AIServiceException):
    code = "INSUFFICIENT_CONTEXT"
    status_code = 422
