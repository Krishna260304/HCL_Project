from typing import Any, Dict, Optional
from core.constants import Roles
from core.exceptions import AuthenticationError, AuthorizationError

def require_authenticated(user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not user or not user.get('user_id'):
        raise AuthenticationError('Authentication credentials were not provided or are invalid.')
    return user

def require_admin(user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    authenticated_user = require_authenticated(user)
    if authenticated_user.get('role') != Roles.ADMIN:
        raise AuthorizationError('Administrator privileges are required to perform this action.')
    return authenticated_user

def require_learner(user: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    authenticated_user = require_authenticated(user)
    if authenticated_user.get('role') != Roles.LEARNER and authenticated_user.get('role') != Roles.ADMIN:
        raise AuthorizationError('Learner access is required.')
    return authenticated_user

def require_owner_or_admin(user: Optional[Dict[str, Any]], resource_owner_id: str) -> Dict[str, Any]:
    authenticated_user = require_authenticated(user)
    if authenticated_user.get('role') == Roles.ADMIN:
        return authenticated_user
    if str(authenticated_user.get('user_id')) != str(resource_owner_id):
        raise AuthorizationError('You do not have permission to access or modify this resource.')
    return authenticated_user
