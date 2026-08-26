from typing import Any, Dict
from core.validators import validate_required_fields, validate_object_id

def validate_moderation_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['target_type', 'target_id', 'reason'])
    return {
        'target_type': str(data['target_type']).strip(),
        'target_id': str(data['target_id']).strip(),
        'reason': str(data['reason']).strip(),
        'details': data.get('details', {}) if isinstance(data.get('details'), dict) else {},
    }

def validate_moderation_resolve_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['item_id', 'status'])
    item_id = validate_object_id(data['item_id'], 'item_id')
    return {
        'item_id': item_id,
        'status': str(data['status']).strip(),
        'resolution_notes': str(data.get('resolution_notes', '')).strip(),
    }
