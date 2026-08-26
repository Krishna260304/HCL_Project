from typing import Any, Dict
from core.constants import LearningHistoryType
from core.validators import validate_required_fields, validate_enum, validate_object_id

def validate_learning_history_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['title', 'type'])
    entry_type = validate_enum(data['type'], LearningHistoryType.ALL_TYPES, 'type')
    return {
        'title': str(data['title']).strip(),
        'type': entry_type,
        'provider': str(data.get('provider', '')).strip(),
        'status': str(data.get('status', 'completed')).strip(),
        'completion_date': str(data.get('completion_date', '')).strip(),
        'confidence': max(1, min(5, int(data.get('confidence', 3)))),
        'certificate': data.get('certificate'),
        'url': str(data.get('url', '')).strip(),
        'skills': data.get('skills', []) if isinstance(data.get('skills'), list) else [],
        'notes': str(data.get('notes', '')).strip(),
    }

def validate_learning_history_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['entry_id'])
    entry_id = validate_object_id(data['entry_id'], 'entry_id')
    updates: Dict[str, Any] = {}
    if 'title' in data:
        updates['title'] = str(data['title']).strip()
    if 'type' in data:
        updates['type'] = validate_enum(data['type'], LearningHistoryType.ALL_TYPES, 'type')
    if 'provider' in data:
        updates['provider'] = str(data['provider']).strip()
    if 'status' in data:
        updates['status'] = str(data['status']).strip()
    if 'completion_date' in data:
        updates['completion_date'] = str(data['completion_date']).strip()
    if 'confidence' in data:
        updates['confidence'] = max(1, min(5, int(data['confidence'])))
    if 'certificate' in data:
        updates['certificate'] = data['certificate']
    if 'url' in data:
        updates['url'] = str(data['url']).strip()
    if 'skills' in data and isinstance(data['skills'], list):
        updates['skills'] = data['skills']
    if 'notes' in data:
        updates['notes'] = str(data['notes']).strip()
    return {'entry_id': entry_id, 'updates': updates}
