from typing import Any, Dict
from core.constants import QuestionType
from core.validators import validate_required_fields, validate_enum, validate_object_id

def validate_save_step_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['step', 'answers'])
    if not isinstance(data['answers'], dict):
        raise ValueError('Answers must be a dictionary object.')
    return {
        'step': int(data['step']),
        'answers': data['answers'],
    }

def validate_question_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['question', 'type'])
    q_type = validate_enum(data['type'], QuestionType.ALL_TYPES, 'type')
    return {
        'question': str(data['question']).strip(),
        'description': str(data.get('description', '')).strip(),
        'category': str(data.get('category', 'general')).strip(),
        'type': q_type,
        'options': data.get('options', []) if isinstance(data.get('options'), list) else [],
        'required': bool(data.get('required', False)),
        'order': int(data.get('order', 1)),
        'enabled': bool(data.get('enabled', True)),
    }

def validate_question_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['question_id'])
    question_id = validate_object_id(data['question_id'], 'question_id')
    updates: Dict[str, Any] = {}
    if 'question' in data:
        updates['question'] = str(data['question']).strip()
    if 'description' in data:
        updates['description'] = str(data['description']).strip()
    if 'category' in data:
        updates['category'] = str(data['category']).strip()
    if 'type' in data:
        updates['type'] = validate_enum(data['type'], QuestionType.ALL_TYPES, 'type')
    if 'options' in data and isinstance(data['options'], list):
        updates['options'] = data['options']
    if 'required' in data:
        updates['required'] = bool(data['required'])
    if 'order' in data:
        updates['order'] = int(data['order'])
    if 'enabled' in data:
        updates['enabled'] = bool(data['enabled'])
    return {'question_id': question_id, 'updates': updates}
