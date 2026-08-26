from typing import Any, Dict
from ai_integrations.client import BaseAIClient
from ai_integrations.exceptions import ExternalAIServiceUnavailableError

class AdaptiveLearningClient:
    endpoint = 'adaptive-learning/evaluate'

    @classmethod
    def evaluate_adaptation(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            raw_response = BaseAIClient.post(cls.endpoint, payload)
            return raw_response
        except ExternalAIServiceUnavailableError:
            return {
                're_rank_resources': True,
                'adjust_roadmap': False,
                'reason': 'Deterministic progress evaluated',
            }
