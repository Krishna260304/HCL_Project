from typing import Any, Dict, Optional
from core.permissions import require_authenticated
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from core.constants import EventNames
from notifications.repository import NotificationRepository
from notifications.validators import validate_notification_create_payload

class NotificationService:
    @classmethod
    def list_notifications(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        unread_only = bool(payload.get('unread_only', False))
        limit = int(payload.get('limit', 50))
        notifications = NotificationRepository.find_by_user_id(user_id, unread_only=unread_only, limit=limit)
        return {'notifications': serialize_mongo_list(notifications)}

    @classmethod
    def mark_as_read(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        notification_id = payload.get('notification_id')
        success = NotificationRepository.mark_as_read(notification_id, user_id)
        return {'notification_id': notification_id, 'read': success}

    @classmethod
    def mark_all_as_read(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        modified_count = NotificationRepository.mark_all_as_read(user_id)
        return {'modified_count': modified_count, 'all_read': True}

    @classmethod
    def create_and_send(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        validated = validate_notification_create_payload(data)
        notif_id = NotificationRepository.create_notification(validated)
        created = NotificationRepository.find_by_user_id(validated['user_id'], limit=1)
        doc = serialize_mongo_doc(created[0]) if created else {'id': notif_id, **validated}
        return doc
