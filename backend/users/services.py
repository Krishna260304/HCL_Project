from typing import Any, Dict, Optional
from core.constants import Roles, UserStatus
from core.exceptions import NotFoundError, AuthorizationError, AuthenticationError
from core.permissions import require_authenticated, require_admin
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from users.repository import UserRepository
from users.validators import validate_user_query_params, validate_user_status_update_payload, validate_user_preferences_payload

class UserService:
    @classmethod
    def get_user_self(cls, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user = UserRepository.find_by_id(auth_user['user_id'])
        if not user:
            raise NotFoundError('User not found.')

        sanitized = serialize_mongo_doc(user)
        sanitized.pop('password_hash', None)
        return sanitized

    @classmethod
    def update_preferences(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        data = validate_user_preferences_payload(payload)
        user_id = auth_user['user_id']
        UserRepository.update_user(user_id, {'preferences': data['preferences']})
        return {'updated': True, 'preferences': data['preferences']}

    @classmethod
    def get_user_by_id(cls, user_id: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        user = UserRepository.find_by_id(user_id)
        if not user:
            raise NotFoundError('User not found.')
        doc = serialize_mongo_doc(user)
        doc.pop('password_hash', None)
        return doc

    @classmethod
    def list_users(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        parsed = validate_user_query_params(payload)
        query = parsed['query']
        pagination = parsed['pagination']

        total = UserRepository.count(query)
        users = UserRepository.find_all(query, skip=pagination['skip'], limit=pagination['page_size'])
        serialized_users = serialize_mongo_list(users)
        for u in serialized_users:
            u.pop('password_hash', None)

        return {
            'total': total,
            'page': pagination['page'],
            'page_size': pagination['page_size'],
            'users': serialized_users,
        }

    @classmethod
    def update_status(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_user_status_update_payload(payload)
        user_id = data['user_id']
        status = data['status']

        user = UserRepository.find_by_id(user_id)
        if not user:
            raise NotFoundError('User not found.')

        UserRepository.update_user(user_id, {'status': status})

        from audit.services import AuditService
        AuditService.log_action(
            admin_id=user_context['user_id'],
            action='user.status_updated',
            module='users',
            target_type='user',
            target_id=user_id,
            before={'status': user.get('status')},
            after={'status': status, 'reason': data.get('reason')}
        )

        return {'user_id': user_id, 'status': status, 'updated': True}

    @classmethod
    def delete_user(cls, user_id: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        user = UserRepository.find_by_id(user_id)
        if not user:
            raise NotFoundError('User not found.')

        UserRepository.delete_user(user_id)

        from audit.services import AuditService
        AuditService.log_action(
            admin_id=user_context['user_id'],
            action='user.deleted',
            module='users',
            target_type='user',
            target_id=user_id,
            before={'email': user.get('email'), 'role': user.get('role')},
            after=None
        )

        return {'user_id': user_id, 'deleted': True}
