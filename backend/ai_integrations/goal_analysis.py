from typing import Any, Dict
from ai_integrations.client import BaseAIClient
from ai_integrations.exceptions import ExternalAIServiceUnavailableError

class GoalAnalysisClient:
    endpoint = 'goal-analysis'

    @classmethod
    def analyze_goal(cls, description: str) -> Dict[str, Any]:
        payload = {'description': description}
        try:
            raw_response = BaseAIClient.post(cls.endpoint, payload)
            return cls.normalize_response(raw_response, description)
        except ExternalAIServiceUnavailableError:
            return cls.fallback_response(description)

    @classmethod
    def normalize_response(cls, response: Dict[str, Any], raw_description: str) -> Dict[str, Any]:
        return {
            'goal': response.get('goal', raw_description),
            'goal_type': response.get('goal_type', 'career_advancement'),
            'target_outcome': response.get('target_outcome', 'Full proficiency'),
            'timeline': response.get('timeline', '3-6 months'),
            'required_skills': response.get('required_skills', []),
            'recommended_domains': response.get('recommended_domains', []),
        }

    @classmethod
    def fallback_response(cls, description: str) -> Dict[str, Any]:
        return {
            'goal': description,
            'goal_type': 'general_learning',
            'target_outcome': 'Competence and practical application',
            'timeline': '3 months',
            'required_skills': [],
            'recommended_domains': [],
        }
