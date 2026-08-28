from typing import Any, Dict
from core.validators import validate_required_fields, validate_object_id

def validate_course_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['title'])
    return {
        'title': str(data['title']).strip(),
        'description': str(data.get('description', '')).strip(),
        'provider': str(data.get('provider', 'internal')).strip(),
        'difficulty': str(data.get('difficulty', 'beginner')).strip(),
        'duration': max(0, int(data.get('duration', 0))),
        'skills': data.get('skills', []) if isinstance(data.get('skills'), list) else [],
        'prerequisites': data.get('prerequisites', []) if isinstance(data.get('prerequisites'), list) else [],
        'learning_objectives': data.get('learning_objectives', []) if isinstance(data.get('learning_objectives'), list) else [],
        'status': str(data.get('status', 'published')).strip(),
        'modules': data.get('modules', []) if isinstance(data.get('modules'), list) else [],
    }

def validate_course_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['course_id'])
    course_id = validate_object_id(data['course_id'], 'course_id')
    updates: Dict[str, Any] = {}
    for key in ('title', 'description', 'provider', 'difficulty', 'status'):
        if key in data:
            updates[key] = str(data[key]).strip()
    if 'duration' in data:
        updates['duration'] = max(0, int(data['duration']))
    if 'skills' in data and isinstance(data['skills'], list):
        updates['skills'] = data['skills']
    if 'prerequisites' in data and isinstance(data['prerequisites'], list):
        updates['prerequisites'] = data['prerequisites']
    if 'learning_objectives' in data and isinstance(data['learning_objectives'], list):
        updates['learning_objectives'] = data['learning_objectives']
    if 'modules' in data and isinstance(data['modules'], list):
        updates['modules'] = data['modules']
    return {'course_id': course_id, 'updates': updates}

def validate_module_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['course_id', 'title'])
    course_id = validate_object_id(data['course_id'], 'course_id')
    return {
        'course_id': course_id,
        'title': str(data['title']).strip(),
        'description': str(data.get('description', '')).strip(),
        'order': int(data.get('order', 1)),
        'resources': data.get('resources', []) if isinstance(data.get('resources'), list) else [],
        'skills': data.get('skills', []) if isinstance(data.get('skills'), list) else [],
        'assessment_id': data.get('assessment_id'),
    }
