from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class GoalRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.GOALS)

    @classmethod
    def find_by_id(cls, goal_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(goal_id):
            return None
        return cls.get_collection().find_one({'_id': ObjectId(goal_id)})

    @classmethod
    def find_by_user_id(cls, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {'user_id': str(user_id)}
        if status:
            query['status'] = status
        cursor = cls.get_collection().find(query).sort('created_at', -1)
        return list(cursor)

    @classmethod
    def create_goal(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_goal(cls, goal_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(goal_id):
            return False
        updates['updated_at'] = now_utc()
        result = cls.get_collection().update_one(
            {'_id': ObjectId(goal_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def delete_goal(cls, goal_id: str) -> bool:
        if not ObjectId.is_valid(goal_id):
            return False
        result = cls.get_collection().delete_one({'_id': ObjectId(goal_id)})
        return result.deleted_count > 0
