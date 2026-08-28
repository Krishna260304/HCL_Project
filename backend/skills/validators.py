from typing import Any, Dict
from core.constants import RelationshipType
from core.validators import validate_required_fields, validate_enum, validate_object_id

def validate_skill_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['name', 'category'])
    return {
        'name': str(data['name']).strip(),
        'description': str(data.get('description', '')).strip(),
        'category': str(data['category']).strip(),
        'tags': data.get('tags', []) if isinstance(data.get('tags'), list) else [],
        'difficulty': str(data.get('difficulty', 'beginner')).strip(),
        'required_level': int(data.get('required_level', 1)),
        'learning_objectives': data.get('learning_objectives', []) if isinstance(data.get('learning_objectives'), list) else [],
        'status': str(data.get('status', 'active')).strip(),
    }

def validate_skill_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['skill_id'])
    skill_id = validate_object_id(data['skill_id'], 'skill_id')
    updates: Dict[str, Any] = {}
    if 'name' in data:
        updates['name'] = str(data['name']).strip()
    if 'description' in data:
        updates['description'] = str(data['description']).strip()
    if 'category' in data:
        updates['category'] = str(data['category']).strip()
    if 'tags' in data and isinstance(data['tags'], list):
        updates['tags'] = data['tags']
    if 'difficulty' in data:
        updates['difficulty'] = str(data['difficulty']).strip()
    if 'required_level' in data:
        updates['required_level'] = int(data['required_level'])
    if 'learning_objectives' in data and isinstance(data['learning_objectives'], list):
        updates['learning_objectives'] = data['learning_objectives']
    if 'status' in data:
        updates['status'] = str(data['status']).strip()
    return {'skill_id': skill_id, 'updates': updates}

def validate_relationship_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['source_skill_id', 'target_skill_id', 'relationship_type'])
    source_id = validate_object_id(data['source_skill_id'], 'source_skill_id')
    target_id = validate_object_id(data['target_skill_id'], 'target_skill_id')
    rel_type = validate_enum(data['relationship_type'], RelationshipType.ALL_TYPES, 'relationship_type')
    return {
        'source_skill_id': source_id,
        'target_skill_id': target_id,
        'relationship_type': rel_type,
    }
