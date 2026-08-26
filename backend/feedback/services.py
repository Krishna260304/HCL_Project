from typing import Any, Dict, Optional
from core.permissions import require_authenticated, require_admin
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from feedback.repository import FeedbackRepository
from feedback.validators import validate_feedback_create_payload

class FeedbackService:
    @classmethod
    def create_feedback(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        data = validate_feedback_create_payload(payload)
        data['user_id'] = auth_user['user_id']
        feedback_id = FeedbackRepository.create_feedback(data)
        return {'feedback_id': feedback_id, 'created': True}

    @classmethod
    def list_self_feedback(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        feedback_items = FeedbackRepository.find_by_user_id(auth_user['user_id'])
        return {'feedback': serialize_mongo_list(feedback_items)}

    @classmethod
    def list_feedback_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        query: Dict[str, Any] = {}
        if 'type' in payload and payload['type']:
            query['type'] = payload['type']
        items = FeedbackRepository.find_all(query)
        return {'feedback': serialize_mongo_list(items)}
