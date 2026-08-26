from typing import Any, Dict, List
from django.conf import settings

class GitHubProvider:
    provider_name = 'github'

    @classmethod
    def get_token(cls) -> str:
        return getattr(settings, 'GITHUB_API_TOKEN', '')

    @classmethod
    def search(cls, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        return []

    @classmethod
    def get_resource(cls, repo_full_name: str) -> Dict[str, Any]:
        return {
            'source': cls.provider_name,
            'source_id': repo_full_name,
            'title': repo_full_name,
            'url': f'https://github.com/{repo_full_name}',
            'type': 'project',
        }

    @classmethod
    def normalize_resource(cls, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'source': cls.provider_name,
            'source_id': raw_data.get('id', ''),
            'title': raw_data.get('name', ''),
            'description': raw_data.get('description', ''),
            'url': raw_data.get('html_url', ''),
            'type': 'project',
            'duration': 0,
            'difficulty': 'intermediate',
            'tags': raw_data.get('topics', []),
        }
