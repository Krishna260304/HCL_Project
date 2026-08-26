from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class FeedbackRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.FEEDBACK)

    @classmethod
    def create_feedback(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def find_by_user_id(cls, user_id: str) -> List[Dict[str, Any]]:
        cursor = cls.get_collection().find({'user_id': str(user_id)}).sort('created_at', -1)
        return list(cursor)

    @classmethod
    def find_all(cls, query: Dict[str, Any], skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = cls.get_collection().find(query).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)
