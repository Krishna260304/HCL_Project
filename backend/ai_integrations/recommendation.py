from typing import Any, Dict, List
from ai_integrations.client import BaseAIClient
from ai_integrations.exceptions import ExternalAIServiceUnavailableError

class RecommendationClient:
    endpoint = 'recommendation'

    @classmethod
    def get_recommendations(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            raw_response = BaseAIClient.post(cls.endpoint, payload, timeout=60)
            return cls.normalize_response(raw_response, payload)
        except Exception:
            return cls.fallback_response(payload)

    @classmethod
    def normalize_response(cls, response: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'recommendations': response.get('recommendations', []),
            'metadata': response.get('metadata', {}),
        }

    @classmethod
    def fallback_response(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        candidate_resources = payload.get('candidate_resources', [])
        recs = []
        for res in candidate_resources[:5]:
            recs.append({
                'resource_id': str(res.get('_id', res.get('id', ''))),
                'skill_id': res.get('skills', ['general'])[0] if res.get('skills') else 'general',
                'score': res.get('quality_score', 0.85),
                'reason': f"Curated resource for {res.get('title')}",
                'source': 'heuristic_ranking',
            })
        return {'recommendations': recs, 'metadata': {'fallback': True}}
