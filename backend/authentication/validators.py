from typing import Any, Dict
from core.constants import ExperienceLevel
from core.validators import validate_required_fields, validate_email, validate_password_strength, validate_enum

def validate_register_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['email', 'password', 'name'])
    email = validate_email(data['email'])
    password = data['password']
    validate_password_strength(password)
    name = str(data['name']).strip()
    return {
        'email': email,
        'password': password,
        'name': name,
        'current_role': str(data.get('current_role', '')).strip(),
        'experience_level': validate_enum(data.get('experience_level', 'beginner'), ExperienceLevel.ALL_LEVELS, 'experience_level'),
        'target_outcome': str(data.get('target_outcome', '')).strip(),
        'age_range': data.get('age_range'),
        'country': data.get('country'),
        'language': data.get('language', 'en'),
    }

def validate_login_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['email', 'password'])
    email = validate_email(data['email'])
    password = data['password']
    return {
        'email': email,
        'password': password,
    }

def validate_refresh_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['refresh_token'])
    return {
        'refresh_token': str(data['refresh_token']).strip(),
    }

def validate_password_reset_request_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['email'])
    email = validate_email(data['email'])
    return {'email': email}

def validate_password_reset_confirm_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['token', 'new_password'])
    validate_password_strength(data['new_password'])
    return {
        'token': str(data['token']).strip(),
        'new_password': str(data['new_password']),
    }

def validate_change_password_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['current_password', 'new_password'])
    validate_password_strength(data['new_password'])
    return {
        'current_password': str(data['current_password']),
        'new_password': str(data['new_password']),
    }
