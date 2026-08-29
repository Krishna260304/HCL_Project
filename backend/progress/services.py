from typing import Any, Dict, Optional
from core.permissions import require_authenticated, require_owner_or_admin
from core.utilities import serialize_mongo_doc, serialize_mongo_list, now_utc
from progress.repository import ProgressRepository
from progress.validators import validate_progress_update_payload

class ProgressService:
    @classmethod
    def get_progress(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        target_user_id = payload.get('user_id', user_id)
        require_owner_or_admin(user_context, target_user_id)

        path_id = payload.get('learning_path_id')
        if path_id:
            progress = ProgressRepository.find_progress_by_path(target_user_id, path_id)
            return {'progress': serialize_mongo_doc(progress)}
        all_prog = ProgressRepository.find_all_user_progress(target_user_id)
        return {'progress_list': serialize_mongo_list(all_prog)}

    @classmethod
    def update_progress(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        data = validate_progress_update_payload(payload)

        updates = {
            'phase_id': data['phase_id'],
            'resource_id': data['resource_id'],
            'progress_percentage': data['progress_percentage'],
            'status': data['status'],
            'time_spent': data['time_spent'],
            'completed_at': now_utc() if data['progress_percentage'] >= 100.0 else None,
        }
        ProgressRepository.update_progress(str(user_id), data['learning_path_id'], updates)
        ProgressRepository.log_activity(str(user_id), {
            'type': 'resource_progress',
            'learning_path_id': data['learning_path_id'],
            'resource_id': data['resource_id'],
            'progress_percentage': data['progress_percentage'],
            'time_spent': data['time_spent'],
        })

        updated = ProgressRepository.find_progress_by_path(str(user_id), data['learning_path_id'])
        return serialize_mongo_doc(updated)

    @classmethod
    def get_skill_progress(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        target_user_id = payload.get('user_id', user_id)
        require_owner_or_admin(user_context, target_user_id)

        skill_progress = ProgressRepository.find_skill_progress_by_user(target_user_id)
        return {'skill_progress': serialize_mongo_list(skill_progress)}

    @classmethod
    def get_activity(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        target_user_id = payload.get('user_id', user_id)
        require_owner_or_admin(user_context, target_user_id)

        limit = int(payload.get('limit', 50))
        activity = ProgressRepository.find_activity_by_user(target_user_id, limit=limit)
        return {'activity': serialize_mongo_list(activity)}
