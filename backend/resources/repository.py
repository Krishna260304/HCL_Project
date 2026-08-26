from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class ResourceRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.RESOURCES)

    @classmethod
    def find_by_id(cls, resource_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(resource_id):
            return None
        return cls.get_collection().find_one({'_id': ObjectId(resource_id)})

    @classmethod
    def find_all(cls, query: Dict[str, Any], skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        cursor = cls.get_collection().find(query).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)

    @classmethod
    def count(cls, query: Dict[str, Any]) -> int:
        return cls.get_collection().count_documents(query)

    @classmethod
    def search(
        cls,
        text_query: Optional[str] = None,
        skills: Optional[List[str]] = None,
        difficulty: Optional[str] = None,
        res_type: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        query: Dict[str, Any] = {}
        if status:
            query['status'] = status
        if text_query:
            query['$or'] = [
                {'title': {'$regex': text_query, '$options': 'i'}},
                {'description': {'$regex': text_query, '$options': 'i'}},
                {'tags': {'$in': [text_query]}},
            ]
        if skills:
            query['skills'] = {'$in': skills}
        if difficulty:
            query['difficulty'] = difficulty
        if res_type:
            query['type'] = res_type

        cursor = cls.get_collection().find(query).sort('quality_score', -1).skip(skip).limit(limit)
        return list(cursor)

    @classmethod
    def create_resource(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_resource(cls, resource_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(resource_id):
            return False
        updates['updated_at'] = now_utc()
        result = cls.get_collection().update_one(
            {'_id': ObjectId(resource_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def delete_resource(cls, resource_id: str) -> bool:
        if not ObjectId.is_valid(resource_id):
            return False
        result = cls.get_collection().delete_one({'_id': ObjectId(resource_id)})
        return result.deleted_count > 0
