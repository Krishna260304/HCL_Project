from typing import Any, Dict
from core.constants import ExperienceLevel
from core.validators import validate_enum, validate_required_fields

ALLOWED_PROFILE_FIELDS = {
    'name',
    'age_range',
    'country',
    'language',
    'education',
    'academic_background',
    'current_status',
    'current_role',
    'experience_years',
    'experience_level',
    'goals',
    'interests',
    'knowledge_areas',
    'learning_preferences',
    'learning_constraints',
    'motivation',
    'target_outcome',
    'timeline',
    'available_hours',
    'practical_experience',
    'self_reported_skills',
}

def validate_profile_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError('Profile update payload must be a dictionary object.')

    updates: Dict[str, Any] = {}
    for key, value in data.items():
        if key in ALLOWED_PROFILE_FIELDS:
            if key == 'experience_level' and value is not None:
                updates[key] = validate_enum(value, ExperienceLevel.ALL_LEVELS, 'experience_level')
            elif key == 'experience_years' and value is not None:
                updates[key] = max(0, int(value))
            elif key == 'available_hours' and value is not None:
                updates[key] = max(1, min(168, int(value)))
            elif key in ('goals', 'interests', 'knowledge_areas', 'practical_experience', 'self_reported_skills'):
                updates[key] = value if isinstance(value, list) else []
            elif key in ('learning_preferences', 'learning_constraints'):
                updates[key] = value if isinstance(value, dict) else {}
            else:
                updates[key] = value
    return updates
