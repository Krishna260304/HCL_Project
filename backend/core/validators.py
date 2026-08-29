import re
from typing import Any, Dict, List, Optional
from bson import ObjectId
from core.exceptions import ValidationError

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    if not isinstance(data, dict):
        raise ValidationError('Payload must be a key-value object.')
    missing = [field for field in required_fields if field not in data or data[field] is None or (isinstance(data[field], str) and data[field].strip() == '')]
    if missing:
        raise ValidationError(
            f'Missing required fields: {", ".join(missing)}',
            details={'missing_fields': missing}
        )

def validate_email(email: str) -> str:
    if not isinstance(email, str) or not EMAIL_REGEX.match(email.strip()):
        raise ValidationError('Invalid email format.', details={'field': 'email', 'value': email})
    return email.strip().lower()

def validate_password_strength(password: str) -> None:
    if not isinstance(password, str) or len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.', details={'field': 'password'})

def validate_enum(value: Any, enum_values: List[Any], field_name: str = 'field') -> Any:
    if value not in enum_values:
        raise ValidationError(
            f'Invalid value "{value}" for {field_name}. Allowed values: {", ".join(map(str, enum_values))}',
            details={'field': field_name, 'allowed_values': enum_values, 'provided_value': value}
        )
    return value

def validate_object_id(id_str: Any, field_name: str = 'id') -> str:
    if not id_str or not isinstance(id_str, str) or not ObjectId.is_valid(id_str):
        raise ValidationError(
            f'Invalid ObjectId format for {field_name}.',
            details={'field': field_name, 'provided_value': id_str}
        )
    return id_str

def validate_pagination_params(data: Dict[str, Any]) -> Dict[str, int]:
    try:
        page = int(data.get('page', 1))
        page_size = int(data.get('page_size', 20))
    except (ValueError, TypeError):
        raise ValidationError('Pagination parameters page and page_size must be integers.')
    page = max(1, page)
    page_size = max(1, min(100, page_size))
    return {'page': page, 'page_size': page_size, 'skip': (page - 1) * page_size}
