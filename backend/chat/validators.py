from typing import Any, Dict
from core.validators import validate_required_fields, validate_object_id

def validate_chat_send_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['message'])
    return {
        'conversation_id': str(data.get('conversation_id', '')).strip() if data.get('conversation_id') else None,
        'message': str(data['message']).strip(),
        'context': data.get('context', {}) if isinstance(data.get('context'), dict) else {},
    }

def validate_create_conversation_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        'title': str(data.get('title', 'New Chat Session')).strip(),
        'metadata': data.get('metadata', {}) if isinstance(data.get('metadata'), dict) else {},
    }
