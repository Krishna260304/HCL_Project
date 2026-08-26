from typing import Any, Dict, List
from django.conf import settings

class KaggleProvider:
    provider_name = 'kaggle'

    @classmethod
    def get_api_key(cls) -> str:
        return getattr(settings, 'KAGGLE_API_KEY', '')

    @classmethod
    def search(cls, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        return []

    @classmethod
    def get_resource(cls, resource_id: str) -> Dict[str, Any]:
        return {
            'source': cls.provider_name,
            'source_id': resource_id,
            'title': resource_id,
            'url': f'https://www.kaggle.com/{resource_id}',
            'type': 'lab',
        }

    @classmethod
    def normalize_resource(cls, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'source': cls.provider_name,
            'source_id': raw_data.get('id', ''),
            'title': raw_data.get('title', ''),
            'description': raw_data.get('description', ''),
            'url': raw_data.get('url', ''),
            'type': 'lab',
            'duration': 0,
            'difficulty': 'advanced',
            'tags': raw_data.get('tags', []),
        }
