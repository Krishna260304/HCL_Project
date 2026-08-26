from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class OnboardingRepository:
    @staticmethod
    def get_sessions_collection():
        return get_collection(Collections.ONBOARDING_SESSIONS)

    @staticmethod
    def get_questions_collection():
        return get_collection(Collections.ONBOARDING_QUESTIONS)

    @classmethod
    def find_session_by_user_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        return cls.get_sessions_collection().find_one({'user_id': str(user_id)})

    @classmethod
    def create_session(cls, doc: Dict[str, Any]) -> str:
        doc['started_at'] = now_utc()
        result = cls.get_sessions_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_session(cls, user_id: str, updates: Dict[str, Any]) -> bool:
        updates['updated_at'] = now_utc()
        result = cls.get_sessions_collection().update_one(
            {'user_id': str(user_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def list_questions(cls, enabled_only: bool = True) -> List[Dict[str, Any]]:
        query = {'enabled': True} if enabled_only else {}
        cursor = cls.get_questions_collection().find(query).sort('order', 1)
        return list(cursor)

    @classmethod
    def find_question_by_id(cls, question_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(question_id):
            return None
        return cls.get_questions_collection().find_one({'_id': ObjectId(question_id)})

    @classmethod
    def create_question(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_questions_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_question(cls, question_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(question_id):
            return False
        updates['updated_at'] = now_utc()
        result = cls.get_questions_collection().update_one(
            {'_id': ObjectId(question_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def delete_question(cls, question_id: str) -> bool:
        if not ObjectId.is_valid(question_id):
            return False
        result = cls.get_questions_collection().delete_one({'_id': ObjectId(question_id)})
        return result.deleted_count > 0
