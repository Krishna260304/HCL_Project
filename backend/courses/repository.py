from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class CourseRepository:
    @staticmethod
    def get_courses_collection():
        return get_collection(Collections.COURSES)

    @staticmethod
    def get_modules_collection():
        return get_collection(Collections.COURSE_MODULES)

    @classmethod
    def find_by_id(cls, course_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(course_id):
            return None
        return cls.get_courses_collection().find_one({'_id': ObjectId(course_id)})

    @classmethod
    def find_all(cls, query: Dict[str, Any], skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        cursor = cls.get_courses_collection().find(query).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)

    @classmethod
    def create_course(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_courses_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_course(cls, course_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(course_id):
            return False
        updates['updated_at'] = now_utc()
        result = cls.get_courses_collection().update_one(
            {'_id': ObjectId(course_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def delete_course(cls, course_id: str) -> bool:
        if not ObjectId.is_valid(course_id):
            return False
        cls.get_modules_collection().delete_many({'course_id': str(course_id)})
        result = cls.get_courses_collection().delete_one({'_id': ObjectId(course_id)})
        return result.deleted_count > 0

    @classmethod
    def find_modules_by_course(cls, course_id: str) -> List[Dict[str, Any]]:
        cursor = cls.get_modules_collection().find({'course_id': str(course_id)}).sort('order', 1)
        return list(cursor)

    @classmethod
    def create_module(cls, doc: Dict[str, Any]) -> str:
        result = cls.get_modules_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_module(cls, module_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(module_id):
            return False
        result = cls.get_modules_collection().update_one(
            {'_id': ObjectId(module_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def delete_module(cls, module_id: str) -> bool:
        if not ObjectId.is_valid(module_id):
            return False
        result = cls.get_modules_collection().delete_one({'_id': ObjectId(module_id)})
        return result.deleted_count > 0
