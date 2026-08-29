from typing import Any, Dict
from core.constants import GoalStatus
from core.validators import validate_required_fields, validate_enum, validate_object_id

def validate_create_goal_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['title'])
    title = str(data['title']).strip()
    status = validate_enum(data.get('status', GoalStatus.ACTIVE), GoalStatus.ALL_STATUSES, 'status')
    return {
        'title': title,
        'description': str(data.get('description', '')).strip(),
        'goal_type': str(data.get('goal_type', 'career')).strip(),
        'target_outcome': str(data.get('target_outcome', '')).strip(),
        'timeline': str(data.get('timeline', '')).strip(),
        'priority': str(data.get('priority', 'medium')).strip(),
        'status': status,
        'required_skills': data.get('required_skills', []) if isinstance(data.get('required_skills'), list) else [],
    }

def validate_update_goal_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['goal_id'])
    goal_id = validate_object_id(data['goal_id'], 'goal_id')
    updates: Dict[str, Any] = {}
    if 'title' in data:
        updates['title'] = str(data['title']).strip()
    if 'description' in data:
        updates['description'] = str(data['description']).strip()
    if 'goal_type' in data:
        updates['goal_type'] = str(data['goal_type']).strip()
    if 'target_outcome' in data:
        updates['target_outcome'] = str(data['target_outcome']).strip()
    if 'timeline' in data:
        updates['timeline'] = str(data['timeline']).strip()
    if 'priority' in data:
        updates['priority'] = str(data['priority']).strip()
    if 'status' in data:
        updates['status'] = validate_enum(data['status'], GoalStatus.ALL_STATUSES, 'status')
    if 'required_skills' in data and isinstance(data['required_skills'], list):
        updates['required_skills'] = data['required_skills']
    return {'goal_id': goal_id, 'updates': updates}
