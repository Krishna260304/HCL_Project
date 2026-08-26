from typing import Any, Dict, Optional
from core.exceptions import AIServiceError

class ExternalAIServiceUnavailableError(AIServiceError):
    def __init__(self, message: str = 'External AI service is currently unavailable.', details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)

class ExternalAIResponseValidationError(AIServiceError):
    def __init__(self, message: str = 'AI service returned an invalid or malformed response.', details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, details=details)
