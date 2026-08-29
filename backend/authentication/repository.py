from typing import Any, Dict, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class AuthRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.USERS)

    @classmethod
    def find_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        return cls.get_collection().find_one({'email': email.lower()})

    @classmethod
    def find_by_id(cls, user_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(user_id):
            return None
        return cls.get_collection().find_one({'_id': ObjectId(user_id)})

    @classmethod
    def create_user(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_last_login(cls, user_id: str) -> None:
        if ObjectId.is_valid(user_id):
            cls.get_collection().update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'last_login_at': now_utc(), 'updated_at': now_utc()}}
            )

    @classmethod
    def update_password_hash(cls, user_id: str, password_hash: str) -> None:
        if ObjectId.is_valid(user_id):
            cls.get_collection().update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'password_hash': password_hash, 'updated_at': now_utc()}}
            )

    @classmethod
    def update_profile_id(cls, user_id: str, profile_id: str) -> None:
        if ObjectId.is_valid(user_id):
            cls.get_collection().update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'profile_id': profile_id, 'updated_at': now_utc()}}
            )
