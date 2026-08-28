from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class ModerationRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.MODERATION_ITEMS)

    @classmethod
    def create_item(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['status'] = 'pending'
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def find_all(cls, query: Dict[str, Any], skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = cls.get_collection().find(query).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)

    @classmethod
    def update_item_status(cls, item_id: str, status: str, resolved_by: str, resolution_notes: str) -> bool:
        if not ObjectId.is_valid(item_id):
            return False
        result = cls.get_collection().update_one(
            {'_id': ObjectId(item_id)},
            {'$set': {
                'status': status,
                'resolved_by': str(resolved_by),
                'resolution_notes': resolution_notes,
                'resolved_at': now_utc(),
            }}
        )
        return result.matched_count > 0
