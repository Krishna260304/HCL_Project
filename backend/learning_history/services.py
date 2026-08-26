from typing import Any, Dict, Optional
from core.permissions import require_authenticated, require_owner_or_admin
from core.exceptions import NotFoundError
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from learning_history.repository import LearningHistoryRepository
from learning_history.validators import (
    validate_learning_history_create_payload,
    validate_learning_history_update_payload
)

class LearningHistoryService:
    @classmethod
    def create_entry(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        data = validate_learning_history_create_payload(payload)
        data['user_id'] = auth_user['user_id']
        entry_id = LearningHistoryRepository.create_entry(data)
        created = LearningHistoryRepository.find_by_id(entry_id)
        return serialize_mongo_doc(created)

    @classmethod
    def list_entries(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        target_user_id = payload.get('user_id', user_id)
        require_owner_or_admin(user_context, target_user_id)

        entry_type = payload.get('type')
        entries = LearningHistoryRepository.find_by_user_id(target_user_id, entry_type=entry_type)
        return {'history': serialize_mongo_list(entries)}

    @classmethod
    def get_entry(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_authenticated(user_context)
        entry_id = payload.get('entry_id')
        entry = LearningHistoryRepository.find_by_id(entry_id)
        if not entry:
            raise NotFoundError('Learning history entry not found.')

        require_owner_or_admin(user_context, entry['user_id'])
        return serialize_mongo_doc(entry)

    @classmethod
    def update_entry(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_authenticated(user_context)
        data = validate_learning_history_update_payload(payload)
        entry_id = data['entry_id']
        entry = LearningHistoryRepository.find_by_id(entry_id)
        if not entry:
            raise NotFoundError('Learning history entry not found.')

        require_owner_or_admin(user_context, entry['user_id'])
        LearningHistoryRepository.update_entry(entry_id, data['updates'])
        updated = LearningHistoryRepository.find_by_id(entry_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def delete_entry(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_authenticated(user_context)
        entry_id = payload.get('entry_id')
        entry = LearningHistoryRepository.find_by_id(entry_id)
        if not entry:
            raise NotFoundError('Learning history entry not found.')

        require_owner_or_admin(user_context, entry['user_id'])
        LearningHistoryRepository.delete_entry(entry_id)
        return {'entry_id': entry_id, 'deleted': True}
