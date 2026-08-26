from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class ProjectRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.PROJECTS)

    @classmethod
    def find_by_id(cls, project_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(project_id):
            return None
        return cls.get_collection().find_one({'_id': ObjectId(project_id)})

    @classmethod
    def find_all(cls, query: Dict[str, Any], skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        cursor = cls.get_collection().find(query).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)

    @classmethod
    def create_project(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_project(cls, project_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(project_id):
            return False
        updates['updated_at'] = now_utc()
        result = cls.get_collection().update_one(
            {'_id': ObjectId(project_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def delete_project(cls, project_id: str) -> bool:
        if not ObjectId.is_valid(project_id):
            return False
        result = cls.get_collection().delete_one({'_id': ObjectId(project_id)})
        return result.deleted_count > 0
