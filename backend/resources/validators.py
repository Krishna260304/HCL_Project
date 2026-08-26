from typing import Any, Dict
from core.constants import ResourceType, ResourceStatus
from core.validators import validate_required_fields, validate_enum, validate_object_id, validate_pagination_params
from resources.normalization import normalize_resource_data

def validate_resource_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['title', 'url'])
    return normalize_resource_data(data)

def validate_resource_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['resource_id'])
    resource_id = validate_object_id(data['resource_id'], 'resource_id')
    updates: Dict[str, Any] = {}
    for key in ('title', 'description', 'source', 'source_id', 'url', 'difficulty', 'language'):
        if key in data:
            updates[key] = str(data[key]).strip()
    if 'type' in data:
        updates['type'] = validate_enum(data['type'], ResourceType.ALL_TYPES, 'type')
    if 'status' in data:
        updates['status'] = validate_enum(data['status'], ResourceStatus.ALL_STATUSES, 'status')
    if 'duration' in data:
        updates['duration'] = max(0, int(data['duration']))
    if 'quality_score' in data:
        updates['quality_score'] = max(0.0, min(1.0, float(data['quality_score'])))
    if 'skills' in data and isinstance(data['skills'], list):
        updates['skills'] = data['skills']
    if 'tags' in data and isinstance(data['tags'], list):
        updates['tags'] = data['tags']
    if 'metadata' in data and isinstance(data['metadata'], dict):
        updates['metadata'] = data['metadata']
    return {'resource_id': resource_id, 'updates': updates}

def validate_resource_search_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    pagination = validate_pagination_params(data)
    return {
        'text_query': str(data.get('query', '')).strip() if data.get('query') else None,
        'skills': data.get('skills') if isinstance(data.get('skills'), list) else None,
        'difficulty': str(data.get('difficulty')).strip() if data.get('difficulty') else None,
        'type': str(data.get('type')).strip() if data.get('type') else None,
        'pagination': pagination,
    }
