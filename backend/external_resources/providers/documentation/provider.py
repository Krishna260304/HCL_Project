from typing import Any, Dict, List

class DocumentationProvider:
    provider_name = 'documentation'

    @classmethod
    def search(cls, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        return []

    @classmethod
    def get_resource(cls, doc_url: str) -> Dict[str, Any]:
        return {
            'source': cls.provider_name,
            'source_id': doc_url,
            'title': 'Official Documentation',
            'url': doc_url,
            'type': 'documentation',
        }

    @classmethod
    def normalize_resource(cls, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'source': cls.provider_name,
            'source_id': raw_data.get('url', ''),
            'title': raw_data.get('title', 'Official Documentation'),
            'description': raw_data.get('description', ''),
            'url': raw_data.get('url', ''),
            'type': 'documentation',
            'duration': 15,
            'difficulty': raw_data.get('difficulty', 'beginner'),
            'tags': raw_data.get('tags', []),
        }
