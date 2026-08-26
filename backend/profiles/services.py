from typing import Any, Dict, Optional
from core.permissions import require_authenticated, require_owner_or_admin
from core.exceptions import NotFoundError
from core.utilities import serialize_mongo_doc
from core.constants import EventNames
from profiles.repository import ProfileRepository
from profiles.validators import validate_profile_update_payload

class ProfileService:
    @classmethod
    def get_profile(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        target_user_id = payload.get('user_id', user_id)
        require_owner_or_admin(user_context, target_user_id)

        profile = ProfileRepository.find_by_user_id(target_user_id)
        if not profile:
            raise NotFoundError('Profile not found.')
        return serialize_mongo_doc(profile)

    @classmethod
    def update_profile(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        target_user_id = payload.get('user_id', user_id)
        require_owner_or_admin(user_context, target_user_id)

        updates = validate_profile_update_payload(payload.get('profile', payload))
        updated = ProfileRepository.update_by_user_id(target_user_id, updates)
        if not updated:
            raise NotFoundError('Profile not found.')

        fresh_profile = ProfileRepository.find_by_user_id(target_user_id)
        return serialize_mongo_doc(fresh_profile)

    @classmethod
    def get_by_user_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        profile = ProfileRepository.find_by_user_id(user_id)
        return serialize_mongo_doc(profile) if profile else None
