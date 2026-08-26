from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from django.conf import settings
from core.exceptions import AuthenticationError

def get_jwt_secret() -> str:
    return getattr(settings, 'JWT_SECRET_KEY', 'jwt-insecure-secret-learnpath-2026')

def get_jwt_algorithm() -> str:
    return getattr(settings, 'JWT_ALGORITHM', 'HS256')

def generate_access_token(user_id: str, email: str, role: str) -> str:
    lifetime_minutes = getattr(settings, 'JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 60)
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': str(user_id),
        'email': email,
        'role': role,
        'type': 'access',
        'iat': now,
        'exp': now + timedelta(minutes=lifetime_minutes),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=get_jwt_algorithm())

def generate_refresh_token(user_id: str, email: str, role: str) -> str:
    lifetime_days = getattr(settings, 'JWT_REFRESH_TOKEN_LIFETIME_DAYS', 7)
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': str(user_id),
        'email': email,
        'role': role,
        'type': 'refresh',
        'iat': now,
        'exp': now + timedelta(days=lifetime_days),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=get_jwt_algorithm())

def generate_token_pair(user_id: str, email: str, role: str) -> Dict[str, Any]:
    lifetime_minutes = getattr(settings, 'JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 60)
    return {
        'access_token': generate_access_token(user_id, email, role),
        'refresh_token': generate_refresh_token(user_id, email, role),
        'token_type': 'Bearer',
        'expires_in': lifetime_minutes * 60,
    }

def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[get_jwt_algorithm()])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError('Token has expired.')
    except jwt.InvalidTokenError:
        raise AuthenticationError('Invalid token.')

def verify_token(token: str, expected_type: str = 'access') -> Dict[str, Any]:
    payload = decode_token(token)
    if payload.get('type') != expected_type:
        raise AuthenticationError(f'Invalid token type. Expected {expected_type} token.')
    return payload
