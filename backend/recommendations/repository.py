from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class RecommendationRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.RECOMMENDATIONS)

    @classmethod
    def find_by_user_id(cls, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {'user_id': str(user_id)}
        if status:
            query['status'] = status
        cursor = cls.get_collection().find(query).sort('score', -1)
        return list(cursor)

    @classmethod
    def find_by_id(cls, rec_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(rec_id):
            return None
        return cls.get_collection().find_one({'_id': ObjectId(rec_id)})

    @classmethod
    def create_recommendation(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_status(cls, rec_id: str, status: str) -> bool:
        if not ObjectId.is_valid(rec_id):
            return False
        result = cls.get_collection().update_one(
            {'_id': ObjectId(rec_id)},
            {'$set': {'status': status, 'updated_at': now_utc()}}
        )
        return result.matched_count > 0

    @classmethod
    def delete_by_user_id(cls, user_id: str) -> int:
        result = cls.get_collection().delete_many({'user_id': str(user_id)})
        return result.deleted_count
