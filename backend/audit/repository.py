from typing import Any, Dict, List, Optional
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

class AuditRepository:
    @staticmethod
    def get_collection():
        return get_collection(Collections.AUDIT_LOGS)

    @classmethod
    def create_log(cls, doc: Dict[str, Any]) -> str:
        doc['timestamp'] = now_utc()
        result = cls.get_collection().insert_one(doc)
        return str(result.inserted_id)

    @classmethod
    def find_all(cls, query: Dict[str, Any], skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = cls.get_collection().find(query).sort('timestamp', -1).skip(skip).limit(limit)
        return list(cursor)
