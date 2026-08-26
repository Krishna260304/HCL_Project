from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class SkillRepository:
    @staticmethod
    def get_skills_collection():
        return get_collection(Collections.SKILLS)

    @staticmethod
    def get_relationships_collection():
        return get_collection(Collections.SKILL_RELATIONSHIPS)

    @classmethod
    def find_all_skills(cls, query: Optional[Dict[str, Any]] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        cursor = cls.get_skills_collection().find(query or {}).sort('name', 1).skip(skip).limit(limit)
        return list(cursor)

    @classmethod
    def count_skills(cls, query: Optional[Dict[str, Any]] = None) -> int:
        return cls.get_skills_collection().count_documents(query or {})

    @classmethod
    def find_by_id(cls, skill_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(skill_id):
            return None
        return cls.get_skills_collection().find_one({'_id': ObjectId(skill_id)})

    @classmethod
    def find_by_name(cls, name: str) -> Optional[Dict[str, Any]]:
        return cls.get_skills_collection().find_one({'name': {'$regex': f'^{name}$', '$options': 'i'}})

    @classmethod
    def create_skill(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_skills_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_skill(cls, skill_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(skill_id):
            return False
        updates['updated_at'] = now_utc()
        result = cls.get_skills_collection().update_one(
            {'_id': ObjectId(skill_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def delete_skill(cls, skill_id: str) -> bool:
        if not ObjectId.is_valid(skill_id):
            return False
        cls.get_relationships_collection().delete_many({
            '$or': [{'source_skill_id': str(skill_id)}, {'target_skill_id': str(skill_id)}]
        })
        result = cls.get_skills_collection().delete_one({'_id': ObjectId(skill_id)})
        return result.deleted_count > 0

    @classmethod
    def list_relationships(cls, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        cursor = cls.get_relationships_collection().find(query or {})
        return list(cursor)

    @classmethod
    def create_relationship(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        result = cls.get_relationships_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def delete_relationship(cls, source_id: str, target_id: str, rel_type: str) -> bool:
        result = cls.get_relationships_collection().delete_one({
            'source_skill_id': str(source_id),
            'target_skill_id': str(target_id),
            'relationship_type': rel_type,
        })
        return result.deleted_count > 0
