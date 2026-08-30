from typing import Any, Dict
from ai_integrations.client import BaseAIClient
from ai_integrations.exceptions import ExternalAIServiceUnavailableError

class ResourceAnalysisClient:
    endpoint = 'resource-analysis'

    @classmethod
    def analyze_resource(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            raw_response = BaseAIClient.post(cls.endpoint, payload, timeout=60)
            return cls.normalize_response(raw_response)
        except Exception:
            return cls.fallback_response(payload)

    @classmethod
    def normalize_response(cls, response: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'skills': response.get('skills', []),
            'topics': response.get('topics', []),
            'difficulty': response.get('difficulty', 'beginner'),
            'prerequisites': response.get('prerequisites', []),
            'quality_score': response.get('quality_score', 0.85),
            'estimated_duration': response.get('estimated_duration', 30),
            'summary': response.get('summary', ''),
        }

    @classmethod
    def fallback_response(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'skills': payload.get('skills', []),
            'topics': [],
            'difficulty': payload.get('difficulty', 'beginner'),
            'prerequisites': [],
            'quality_score': 0.8,
            'estimated_duration': payload.get('duration', 20),
            'summary': payload.get('description', ''),
        }
