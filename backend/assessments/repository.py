from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class AssessmentRepository:
    @staticmethod
    def get_assessments_col():
        return get_collection(Collections.ASSESSMENTS)

    @staticmethod
    def get_questions_col():
        return get_collection(Collections.QUESTIONS)

    @staticmethod
    def get_attempts_col():
        return get_collection(Collections.ASSESSMENT_ATTEMPTS)

    @staticmethod
    def get_results_col():
        return get_collection(Collections.ASSESSMENT_RESULTS)

    @classmethod
    def find_assessment_by_id(cls, assessment_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(assessment_id):
            return None
        return cls.get_assessments_col().find_one({'_id': ObjectId(assessment_id)})

    @classmethod
    def find_by_id(cls, assessment_id: str) -> Optional[Dict[str, Any]]:
        return cls.find_assessment_by_id(assessment_id)

    @classmethod
    def find_all_assessments(cls, query: Dict[str, Any], skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        cursor = cls.get_assessments_col().find(query).sort('created_at', -1).skip(skip).limit(limit)
        return list(cursor)

    @classmethod
    def create_assessment(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_assessments_col().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_assessment(cls, assessment_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(assessment_id):
            return False
        updates['updated_at'] = now_utc()
        result = cls.get_assessments_col().update_one(
            {'_id': ObjectId(assessment_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def delete_assessment(cls, assessment_id: str) -> bool:
        if not ObjectId.is_valid(assessment_id):
            return False
        result = cls.get_assessments_col().delete_one({'_id': ObjectId(assessment_id)})
        return result.deleted_count > 0

    @classmethod
    def find_questions_by_assessment(cls, assessment_id: str) -> List[Dict[str, Any]]:
        cursor = cls.get_questions_col().find({'assessment_id': str(assessment_id), 'status': 'active'})
        return list(cursor)

    @classmethod
    def find_questions_by_ids(cls, question_ids: List[str]) -> List[Dict[str, Any]]:
        valid_ids = [ObjectId(qid) for qid in question_ids if ObjectId.is_valid(qid)]
        cursor = cls.get_questions_col().find({'_id': {'$in': valid_ids}})
        return list(cursor)

    @classmethod
    def find_question_by_id(cls, question_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(question_id):
            return None
        return cls.get_questions_col().find_one({'_id': ObjectId(question_id)})

    @classmethod
    def create_question(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        doc['updated_at'] = now_utc()
        result = cls.get_questions_col().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def update_question(cls, question_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(question_id):
            return False
        updates['updated_at'] = now_utc()
        result = cls.get_questions_col().update_one(
            {'_id': ObjectId(question_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def delete_question(cls, question_id: str) -> bool:
        if not ObjectId.is_valid(question_id):
            return False
        result = cls.get_questions_col().delete_one({'_id': ObjectId(question_id)})
        return result.deleted_count > 0

    @classmethod
    def create_attempt(cls, doc: Dict[str, Any]) -> str:
        doc['started_at'] = now_utc()
        result = cls.get_attempts_col().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def find_attempt_by_id(cls, attempt_id: str) -> Optional[Dict[str, Any]]:
        if not ObjectId.is_valid(attempt_id):
            return None
        return cls.get_attempts_col().find_one({'_id': ObjectId(attempt_id)})

    @classmethod
    def update_attempt(cls, attempt_id: str, updates: Dict[str, Any]) -> bool:
        if not ObjectId.is_valid(attempt_id):
            return False
        result = cls.get_attempts_col().update_one(
            {'_id': ObjectId(attempt_id)},
            {'$set': updates}
        )
        return result.matched_count > 0

    @classmethod
    def create_result(cls, doc: Dict[str, Any]) -> str:
        doc['created_at'] = now_utc()
        result = cls.get_results_col().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def find_result_by_attempt_id(cls, attempt_id: str) -> Optional[Dict[str, Any]]:
        return cls.get_results_col().find_one({'attempt_id': str(attempt_id)})

    @classmethod
    def find_results_by_user_id(cls, user_id: str) -> List[Dict[str, Any]]:
        cursor = cls.get_results_col().find({'user_id': str(user_id)}).sort('created_at', -1)
        return list(cursor)
