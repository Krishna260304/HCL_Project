from typing import Any, Dict
from core.validators import validate_required_fields, validate_object_id

def validate_path_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['title'])
    return {
        'goal_id': data.get('goal_id'),
        'title': str(data['title']).strip(),
        'description': str(data.get('description', '')).strip(),
        'duration': max(0, int(data.get('duration', 0))),
        'status': str(data.get('status', 'active')).strip(),
        'progress': max(0.0, min(100.0, float(data.get('progress', 0.0)))),
        'phases': data.get('phases', []) if isinstance(data.get('phases'), list) else [],
    }

def validate_path_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['path_id'])
    path_id = validate_object_id(data['path_id'], 'path_id')
    updates: Dict[str, Any] = {}
    if 'title' in data:
        updates['title'] = str(data['title']).strip()
    if 'description' in data:
        updates['description'] = str(data['description']).strip()
    if 'duration' in data:
        updates['duration'] = max(0, int(data['duration']))
    if 'status' in data:
        updates['status'] = str(data['status']).strip()
    if 'progress' in data:
        updates['progress'] = max(0.0, min(100.0, float(data['progress'])))
    if 'phases' in data and isinstance(data['phases'], list):
        updates['phases'] = data['phases']
    return {'path_id': path_id, 'updates': updates}

def validate_phase_action_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['path_id', 'phase_id'])
    return {
        'path_id': validate_object_id(data['path_id'], 'path_id'),
        'phase_id': str(data['phase_id']).strip(),
    }
