from typing import Any, Dict, Optional
from core.constants import ErrorCodes

class BaseAppException(Exception):
    def __init__(
        self,
        message: str,
        code: str = ErrorCodes.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            'code': self.code,
            'message': self.message,
            'details': self.details,
        }

class AuthenticationError(BaseAppException):
    def __init__(self, message: str = 'Authentication failed', details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=ErrorCodes.AUTHENTICATION_ERROR, details=details)

class AuthorizationError(BaseAppException):
    def __init__(self, message: str = 'Permission denied', details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=ErrorCodes.AUTHORIZATION_ERROR, details=details)

class ValidationError(BaseAppException):
    def __init__(self, message: str = 'Validation failed', details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=ErrorCodes.VALIDATION_ERROR, details=details)

class NotFoundError(BaseAppException):
    def __init__(self, message: str = 'Resource not found', details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=ErrorCodes.NOT_FOUND, details=details)

class ConflictError(BaseAppException):
    def __init__(self, message: str = 'Resource already exists or conflict occurred', details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=ErrorCodes.CONFLICT, details=details)

class DatabaseError(BaseAppException):
    def __init__(self, message: str = 'Database operation failed', details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=ErrorCodes.DATABASE_ERROR, details=details)

class ExternalServiceError(BaseAppException):
    def __init__(self, message: str = 'External service communication failed', details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=ErrorCodes.EXTERNAL_SERVICE_ERROR, details=details)

class AIServiceError(BaseAppException):
    def __init__(self, message: str = 'AI service communication failed', details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=ErrorCodes.AI_SERVICE_ERROR, details=details)

class RateLimitError(BaseAppException):
    def __init__(self, message: str = 'Rate limit exceeded', details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, code=ErrorCodes.RATE_LIMIT_ERROR, details=details)
