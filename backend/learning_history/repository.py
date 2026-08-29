from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class LearningHistoryRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.LEARNING_HISTORY)

    @classmethod
    def find_by_id(cls, entry_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(entry_id):
            return None
        return cls.get_collection().find_one({'_id': ObjectId(entry_id)})

    @classmethod
    def find_by_user_id(cls, user_id: str, entry_type: Optional[str] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {'user_id': str(user_id)}
        if entry_type:
            query['type'] = entry_type
        cursor = cls.get_collection().find(query).sort('created_at', -1)
        return list(cursor)

    @classmethod
    def create_entry(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_entry(cls, entry_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(entry_id):
            return False
        updates['updated_at'] = now_utc()
        result = cls.get_collection().update_one(
            {'_id': ObjectId(entry_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def delete_entry(cls, entry_id: str) -> bool:
        if not ObjectId.is_valid(entry_id):
            return False
        result = cls.get_collection().delete_one({'_id': ObjectId(entry_id)})
        return result.deleted_count > 0
