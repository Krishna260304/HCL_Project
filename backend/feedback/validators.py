from typing import Any, Dict
from core.constants import FeedbackType
from core.validators import validate_required_fields, validate_enum

def validate_feedback_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['type', 'rating'])
    f_type = validate_enum(data['type'], FeedbackType.ALL_TYPES, 'type')
    return {
        'type': f_type,
        'resource_id': str(data.get('resource_id', '')).strip() if data.get('resource_id') else None,
        'learning_path_id': str(data.get('learning_path_id', '')).strip() if data.get('learning_path_id') else None,
        'assessment_id': str(data.get('assessment_id', '')).strip() if data.get('assessment_id') else None,
        'rating': max(1, min(5, int(data['rating']))),
        'difficulty': str(data.get('difficulty', '')).strip(),
        'comment': str(data.get('comment', '')).strip(),
    }
