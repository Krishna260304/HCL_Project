from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class ProgressRepository:
    @staticmethod
    def get_progress_col():
        return get_collection(Collections.PROGRESS)

    @staticmethod
    def get_skill_progress_col():
        return get_collection(Collections.SKILL_PROGRESS)

    @staticmethod
    def get_activity_col():
        return get_collection(Collections.LEARNING_ACTIVITY)

    @classmethod
    def find_progress_by_path(cls, user_id: str, learning_path_id: str) -> Optional[Dict[str, Any]]:
        return cls.get_progress_col().find_one({
            'user_id': str(user_id),
            'learning_path_id': str(learning_path_id)
        })

    @classmethod
    def find_all_user_progress(cls, user_id: str) -> List[Dict[str, Any]]:
        cursor = cls.get_progress_col().find({'user_id': str(user_id)})
        return list(cursor)

    @classmethod
    def update_progress(cls, user_id: str, learning_path_id: str, updates: Dict[str, Any]) -> None:
        updates['updated_at'] = now_utc()
        cls.get_progress_col().update_one(
            {'user_id': str(user_id), 'learning_path_id': str(learning_path_id)},
            {'$set': updates, '$setOnInsert': {'started_at': now_utc()}},
            upsert=True
        )

    @classmethod
    def upsert_skill_progress(cls, user_id: str, skill_id: str, data: Dict[str, Any]) -> None:
        data['updated_at'] = now_utc()
        cls.get_skill_progress_col().update_one(
            {'user_id': str(user_id), 'skill_id': str(skill_id)},
            {'$set': data, '$setOnInsert': {'user_id': str(user_id), 'skill_id': str(skill_id)}},
            upsert=True
        )

    @classmethod
    def find_skill_progress_by_user(cls, user_id: str) -> List[Dict[str, Any]]:
        cursor = cls.get_skill_progress_col().find({'user_id': str(user_id)})
        return list(cursor)

    @classmethod
    def log_activity(cls, user_id: str, data: Dict[str, Any]) -> str:
        doc = {
            'user_id': str(user_id),
            'timestamp': now_utc(),
            **data
        }
        result = cls.get_activity_col().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def find_activity_by_user(cls, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = cls.get_activity_col().find({'user_id': str(user_id)}).sort('timestamp', -1).limit(limit)
        return list(cursor)
