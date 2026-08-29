from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class UserRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.USERS)

    @classmethod
    def find_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(user_id):
            return None
        return cls.get_collection().find_one({'_id': ObjectId(user_id)})

    @classmethod
    def find_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        return cls.get_collection().find_one({'email': email.lower()})

    @classmethod
    def find_all(cls, query: Dict[str, Any], skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        cursor = cls.get_collection().find(query).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)

    @classmethod
    def count(cls, query: Dict[str, Any]) -> int:
        return cls.get_collection().count_documents(query)

    @classmethod
    def update_user(cls, user_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        updates['updated_at'] = now_utc()
        result = cls.get_collection().update_one(
            {'_id': ObjectId(user_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def delete_user(cls, user_id: str) -> bool:
        if not ObjectId.is_valid(user_id):
            return False
        result = cls.get_collection().delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0
