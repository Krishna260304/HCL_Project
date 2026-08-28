from typing import Any, Dict, List, Optional
from bson import ObjectId
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class ExternalResourceRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.EXTERNAL_RESOURCES)

    @classmethod
    def find_by_source_and_id(cls, source: str, source_id: str) -> Optional[Dict[str, Any]]:
        return cls.get_collection().find_one({'source': source, 'source_id': source_id})

    @classmethod
    def save_resource(cls, doc: Dict[str, Any]) -> str:
        doc['updated_at'] = now_utc()
        result = cls.get_collection().update_one(
            {'source': doc['source'], 'source_id': doc['source_id']},
            {'$set': doc, '$setOnInsert': {'created_at': now_utc()}},
            upsert=True
        )
        return str(result.upserted_id) if result.upserted_id else ''

    @classmethod
    def list_by_source(cls, source: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = cls.get_collection().find({'source': source}).skip(skip).limit(limit)
        return list(cursor)
