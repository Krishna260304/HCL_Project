from typing import Any, Dict
from ai_integrations.client import BaseAIClient
from ai_integrations.exceptions import ExternalAIServiceUnavailableError

class SkillAnalysisClient:
    endpoint = 'skill-analysis'

    @classmethod
    def analyze_skills(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            raw_response = BaseAIClient.post(cls.endpoint, payload, timeout=60)
            return cls.normalize_response(raw_response)
        except Exception:
            return cls.fallback_response(payload)

    @classmethod
    def normalize_response(cls, response: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'strengths': response.get('strengths', []),
            'weaknesses': response.get('weaknesses', []),
            'skill_gaps': response.get('skill_gaps', []),
            'estimated_skill_levels': response.get('estimated_skill_levels', {}),
            'recommended_next_skills': response.get('recommended_next_skills', []),
        }

    @classmethod
    def fallback_response(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        verified = payload.get('verified_skills', [])
        return {
            'strengths': [s.get('skill_id') for s in verified if s.get('verified_score', 0) >= 70],
            'weaknesses': [s.get('skill_id') for s in verified if s.get('verified_score', 0) < 60],
            'skill_gaps': [],
            'estimated_skill_levels': {s.get('skill_id'): s.get('verified_score') for s in verified if 'skill_id' in s},
            'recommended_next_skills': [],
        }
