from typing import Any, Dict, Optional
from core.permissions import require_authenticated, require_admin
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from moderation.repository import ModerationRepository
from moderation.validators import validate_moderation_create_payload, validate_moderation_resolve_payload

class ModerationService:
    @classmethod
    def flag_content(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        data = validate_moderation_create_payload(payload)
        data['flagged_by'] = auth_user['user_id']
        item_id = ModerationRepository.create_item(data)
        return {'moderation_id': item_id, 'flagged': True}

    @classmethod
    def list_moderation_items(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        query: Dict[str, Any] = {}
        if 'status' in payload and payload['status']:
            query['status'] = payload['status']
        items = ModerationRepository.find_all(query)
        return {'items': serialize_mongo_list(items)}

    @classmethod
    def resolve_item(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_moderation_resolve_payload(payload)
        success = ModerationRepository.update_item_status(
            item_id=data['item_id'],
            status=data['status'],
            resolved_by=user_context['user_id'],
            resolution_notes=data['resolution_notes']
        )
        return {'item_id': data['item_id'], 'resolved': success}
