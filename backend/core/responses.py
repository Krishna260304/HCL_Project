from typing import Any, Dict, Optional
from core.constants import ErrorCodes

def success_response(
    action: str,
    request_id: Optional[str] = None,
    data: Optional[Any] = None
) -> Dict[str, Any]:
    return {
        'type': 'response',
        'action': action,
        'request_id': request_id,
        'success': True,
        'data': data if data is not None else {},
    }

def error_response(
    action: str,
    request_id: Optional[str] = None,
    code: str = ErrorCodes.INTERNAL_ERROR,
    message: str = 'An error occurred',
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    return {
        'type': 'error',
        'action': action,
        'request_id': request_id,
        'success': False,
        'error': {
            'code': code,
            'message': message,
            'details': details or {},
        },
    }

def event_message(event: str, data: Optional[Any] = None) -> Dict[str, Any]:
    return {
        'type': 'event',
        'event': event,
        'data': data if data is not None else {},
    }
