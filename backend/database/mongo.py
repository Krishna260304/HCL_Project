import threading
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from django.conf import settings

_mongo_client: Optional[MongoClient] = None
_lock = threading.Lock()

def get_client() -> MongoClient:
    global _mongo_client
    if _mongo_client is None:
        with _lock:
            if _mongo_client is None:
                uri = getattr(settings, 'MONGODB_URI', 'mongodb://localhost:27017')
                _mongo_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _mongo_client

def get_database(db_name: Optional[str] = None) -> Database:
    client = get_client()
    name = db_name or getattr(settings, 'MONGODB_DATABASE', 'learnpath_ai')
    return client[name]

def get_collection(collection_name: str, db_name: Optional[str] = None) -> Collection:
    db = get_database(db_name)
    return db[collection_name]

def close_mongo_connection() -> None:
    global _mongo_client
    with _lock:
        if _mongo_client is not None:
            _mongo_client.close()
            _mongo_client = None

def set_mongo_client(client: MongoClient) -> None:
    global _mongo_client
    with _lock:
        _mongo_client = client
