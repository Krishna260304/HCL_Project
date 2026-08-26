from typing import Any, Dict
from core.validators import validate_required_fields, validate_object_id

def validate_project_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['title'])
    return {
        'title': str(data['title']).strip(),
        'description': str(data.get('description', '')).strip(),
        'difficulty': str(data.get('difficulty', 'intermediate')).strip(),
        'skills': data.get('skills', []) if isinstance(data.get('skills'), list) else [],
        'prerequisites': data.get('prerequisites', []) if isinstance(data.get('prerequisites'), list) else [],
        'estimated_duration': max(0, int(data.get('estimated_duration', 0))),
        'requirements': data.get('requirements', []) if isinstance(data.get('requirements'), list) else [],
        'deliverables': data.get('deliverables', []) if isinstance(data.get('deliverables'), list) else [],
        'resources': data.get('resources', []) if isinstance(data.get('resources'), list) else [],
        'status': str(data.get('status', 'published')).strip(),
    }

def validate_project_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['project_id'])
    project_id = validate_object_id(data['project_id'], 'project_id')
    updates: Dict[str, Any] = {}
    for key in ('title', 'description', 'difficulty', 'status'):
        if key in data:
            updates[key] = str(data[key]).strip()
    if 'estimated_duration' in data:
        updates['estimated_duration'] = max(0, int(data['estimated_duration']))
    for list_key in ('skills', 'prerequisites', 'requirements', 'deliverables', 'resources'):
        if list_key in data and isinstance(data[list_key], list):
            updates[list_key] = data[list_key]
    return {'project_id': project_id, 'updates': updates}
