from typing import Any, Dict
from core.validators import validate_required_fields

def validate_platform_settings_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    allowed_keys = {
        'platform_name',
        'registration_enabled',
        'learner_login_enabled',
        'ai_enabled',
        'assessment_enabled',
        'recommendation_enabled',
        'resource_discovery_enabled',
        'adaptive_learning_enabled',
        'maintenance_mode',
        'default_language',
        'default_timezone',
    }
    updates: Dict[str, Any] = {}
    for key, value in data.items():
        if key in allowed_keys:
            updates[key] = value
    return updates

def validate_feature_flag_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['name', 'enabled'])
    return {
        'name': str(data['name']).strip(),
        'enabled': bool(data['enabled']),
    }
