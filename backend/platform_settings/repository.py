from typing import Any, Dict, List, Optional
from database.mongo import get_collection
from database.collections import Collections
from core.utilities import now_utc

DEFAULT_SETTINGS = {
    'platform_name': 'LearnPath AI',
    'registration_enabled': True,
    'learner_login_enabled': True,
    'ai_enabled': True,
    'assessment_enabled': True,
    'recommendation_enabled': True,
    'resource_discovery_enabled': True,
    'adaptive_learning_enabled': True,
    'maintenance_mode': False,
    'default_language': 'en',
    'default_timezone': 'UTC',
}

DEFAULT_FEATURE_FLAGS = [
    {'name': 'ai_assistant', 'description': 'Interactive conversational AI tutor', 'enabled': True},
    {'name': 'diagnostic_assessment', 'description': 'Automatic level placement and diagnostic test', 'enabled': True},
    {'name': 'adaptive_learning', 'description': 'Dynamic roadmap adjustments based on assessment results', 'enabled': True},
    {'name': 'recommendations', 'description': 'Personalized AI resource recommendations', 'enabled': True},
    {'name': 'skill_graph', 'description': 'Interactive visual skill dependency graph', 'enabled': True},
    {'name': 'external_resources', 'description': 'YouTube, GitHub, Kaggle and Docs crawler', 'enabled': True},
    {'name': 'projects', 'description': 'Hands-on practical projects catalog', 'enabled': True},
    {'name': 'notifications', 'description': 'Real-time WebSocket notifications', 'enabled': True},
]

class SettingsRepository:
    @staticmethod
    def get_settings_col():
        return get_collection(Collections.PLATFORM_SETTINGS)

    @staticmethod
    def get_flags_col():
        return get_collection(Collections.FEATURE_FLAGS)

    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        settings_doc = cls.get_settings_col().find_one({'key': 'global_config'})
        if not settings_doc:
            doc = {'key': 'global_config', **DEFAULT_SETTINGS, 'updated_at': now_utc()}
            cls.get_settings_col().insert_one(doc)
            return doc
        return settings_doc

    @classmethod
    def update_settings(cls, updates: Dict[str, Any]) -> Dict[str, Any]:
        updates.pop('key', None)
        updates.pop('_id', None)
        updates['updated_at'] = now_utc()
        cls.get_settings_col().update_one(
            {'key': 'global_config'},
            {'$set': updates},
            upsert=True
        )
        return cls.get_settings()

    @classmethod
    def list_flags(cls) -> List[Dict[str, Any]]:
        count = cls.get_flags_col().count_documents({})
        if count == 0:
            for flag in DEFAULT_FEATURE_FLAGS:
                cls.get_flags_col().update_one(
                    {'name': flag['name']},
                    {'$setOnInsert': {**flag, 'updated_at': now_utc()}},
                    upsert=True
                )
        cursor = cls.get_flags_col().find({})
        return list(cursor)

    @classmethod
    def update_flag(cls, name: str, enabled: bool, updated_by: str) -> None:
        cls.get_flags_col().update_one(
            {'name': name},
            {'$set': {'enabled': enabled, 'updated_by': str(updated_by), 'updated_at': now_utc()}},
            upsert=True
        )
