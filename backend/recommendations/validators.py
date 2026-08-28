from typing import Any, Dict
from core.constants import RecommendationStatus
from core.validators import validate_required_fields, validate_enum, validate_object_id

def validate_recommendation_status_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['recommendation_id', 'status'])
    rec_id = validate_object_id(data['recommendation_id'], 'recommendation_id')
    status = validate_enum(data['status'], RecommendationStatus.ALL_STATUSES, 'status')
    return {'recommendation_id': rec_id, 'status': status}
