from typing import Any, Dict
from core.validators import validate_required_fields, validate_object_id

def validate_progress_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['learning_path_id', 'progress_percentage'])
    path_id = validate_object_id(data['learning_path_id'], 'learning_path_id')
    return {
        'learning_path_id': path_id,
        'phase_id': str(data.get('phase_id', '')).strip(),
        'resource_id': str(data.get('resource_id', '')).strip() if data.get('resource_id') else None,
        'progress_percentage': max(0.0, min(100.0, float(data['progress_percentage']))),
        'status': str(data.get('status', 'in_progress')).strip(),
        'time_spent': max(0, int(data.get('time_spent', 0))),
    }
