from typing import Any, Dict, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class ProfileRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.PROFILES)

    @classmethod
    def find_by_user_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        return cls.get_collection().find_one({'user_id': str(user_id)})

    @classmethod
    def find_by_id(cls, profile_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(profile_id):
            return None
        return cls.get_collection().find_one({'_id': ObjectId(profile_id)})

    @classmethod
    def create_profile(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_by_user_id(cls, user_id: str, updates: Dict[str, Any]) -> bool:
        updates['updated_at'] = now_utc()
        result = cls.get_collection().update_one(
            {'user_id': str(user_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def add_verified_skill(cls, user_id: str, skill_data: Dict[str, Any]) -> None:
        skill_id = skill_data['skill_id']
        cls.get_collection().update_one(
            {'user_id': str(user_id)},
            {'$pull': {'verified_skills': {'skill_id': skill_id}}}
        )
        cls.get_collection().update_one(
            {'user_id': str(user_id)},
            {'$push': {'verified_skills': skill_data}, '$set': {'updated_at': now_utc()}}
        )
