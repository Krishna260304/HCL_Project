from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class NotificationRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.NOTIFICATIONS)

    @classmethod
    def create_notification(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['read'] = False
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def find_by_user_id(cls, user_id: str, unread_only: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {'user_id': str(user_id)}
        if unread_only:
            query['read'] = False
        cursor = cls.get_collection().find(query).sort('created_at', -1).limit(limit)
        return list(cursor)

    @classmethod
    def mark_as_read(cls, notification_id: str, user_id: str) -> bool:
        if not ObjectId.is_valid(notification_id):
            return False
        result = cls.get_collection().update_one(
            {'_id': ObjectId(notification_id), 'user_id': str(user_id)},
            {'$set': {'read': True, 'read_at': now_utc()}}
        )
        return result.matched_count > 0

    @classmethod
    def mark_all_as_read(cls, user_id: str) -> int:
        result = cls.get_collection().update_many(
            {'user_id': str(user_id), 'read': False},
            {'$set': {'read': True, 'read_at': now_utc()}}
        )
        return result.modified_count
