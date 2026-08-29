from typing import Any, Dict, List, Optional
from core.permissions import require_authenticated
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from external_resources.repository import ExternalResourceRepository
from external_resources.validators import validate_external_search_payload
from external_resources.providers.youtube.provider import YouTubeProvider
from external_resources.providers.github.provider import GitHubProvider
from external_resources.providers.kaggle.provider import KaggleProvider
from external_resources.providers.documentation.provider import DocumentationProvider

class ExternalResourceService:
    PROVIDERS = {
        'youtube': YouTubeProvider,
        'github': GitHubProvider,
        'kaggle': KaggleProvider,
        'documentation': DocumentationProvider,
    }

    @classmethod
    def search_external(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        data = validate_external_search_payload(payload)
        provider_cls = cls.PROVIDERS.get(data['provider'], YouTubeProvider)
        results = provider_cls.search(data['query'], max_results=data['max_results'])
        return {
            'provider': data['provider'],
            'query': data['query'],
            'results': results,
        }
