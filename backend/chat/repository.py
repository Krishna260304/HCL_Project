from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class ChatRepository:
    @staticmethod
    def get_conv_col():
        return get_collection(Collections.CONVERSATIONS)

    @staticmethod
    def get_msg_col():
        return get_collection(Collections.MESSAGES)

    @classmethod
    def find_conversation_by_id(cls, conv_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(conv_id):
            return None
        return cls.get_conv_col().find_one({'_id': ObjectId(conv_id)})

    @classmethod
    def find_conversations_by_user(cls, user_id: str) -> List[Dict[str, Any]]:
        cursor = cls.get_conv_col().find({'user_id': str(user_id)}).sort('updated_at', -1)
        return list(cursor)

    @classmethod
    def create_conversation(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_conv_col().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_conversation_timestamp(cls, conv_id: str) -> None:
        if ObjectId.is_valid(conv_id):
            cls.get_conv_col().update_one(
                {'_id': ObjectId(conv_id)},
                {'$set': {'updated_at': now_utc()}}
            )

    @classmethod
    def save_message(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        result = cls.get_msg_col().insert_one(doc)
        cls.update_conversation_timestamp(doc.get('conversation_id'))
        return str(result.inserted_id)

    @classmethod
    def find_messages_by_conversation(cls, conv_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = cls.get_msg_col().find({'conversation_id': str(conv_id)}).sort('created_at', 1).limit(limit)
        return list(cursor)
