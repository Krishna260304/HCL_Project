from typing import Any, Dict
from core.constants import UserStatus, Roles
from core.validators import validate_required_fields, validate_enum, validate_pagination_params

def validate_user_status_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['user_id', 'status'])
    status = validate_enum(data['status'], UserStatus.ALL_STATUSES, 'status')
    return {
        'user_id': str(data['user_id']).strip(),
        'status': status,
        'reason': str(data.get('reason', '')).strip(),
    }

def validate_user_preferences_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['preferences'])
    if not isinstance(data['preferences'], dict):
        raise ValueError('Preferences must be a dictionary object.')
    return {
        'preferences': data['preferences']
    }

def validate_user_query_params(data: Dict[str, Any]) -> Dict[str, Any]:
    pagination = validate_pagination_params(data)
    query: Dict[str, Any] = {}
    if 'role' in data and data['role'] in Roles.ALL_ROLES:
        query['role'] = data['role']
    if 'status' in data and data['status'] in UserStatus.ALL_STATUSES:
        query['status'] = data['status']
    if 'search' in data and data['search']:
        query['email'] = {'$regex': str(data['search']).strip(), '$options': 'i'}
    return {
        'query': query,
        'pagination': pagination,
    }
