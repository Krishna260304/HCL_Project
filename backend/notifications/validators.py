from typing import Any, Dict
from core.constants import NotificationType
from core.validators import validate_required_fields, validate_enum, validate_object_id

def validate_notification_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['user_id', 'title', 'message'])
    n_type = validate_enum(data.get('type', NotificationType.SYSTEM), NotificationType.ALL_TYPES, 'type')
    return {
        'user_id': str(data['user_id']).strip(),
        'title': str(data['title']).strip(),
        'message': str(data['message']).strip(),
        'type': n_type,
        'priority': str(data.get('priority', 'normal')).strip(),
        'action_url': str(data.get('action_url', '')).strip(),
    }
