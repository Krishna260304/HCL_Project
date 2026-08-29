from typing import Any, Dict
from ai_integrations.client import BaseAIClient
from ai_integrations.exceptions import ExternalAIServiceUnavailableError

class LearningPathClient:
    endpoint = 'learning-path'

    @classmethod
    def generate_learning_path(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            raw_response = BaseAIClient.post(cls.endpoint, payload)
            return cls.normalize_response(raw_response, payload)
        except ExternalAIServiceUnavailableError:
            return cls.fallback_response(payload)

    @classmethod
    def normalize_response(cls, response: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'title': response.get('title', f"Learning Path: {payload.get('goal', 'Skill Acceleration')}"),
            'description': response.get('description', 'Structured roadmap generated to reach your target outcome.'),
            'estimated_duration_weeks': response.get('estimated_duration_weeks', 8),
            'phases': response.get('phases', []),
        }

    @classmethod
    def fallback_response(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        goal_title = payload.get('goal', 'Skill Acceleration')
        return {
            'title': f"Learning Roadmap: {goal_title}",
            'description': 'A multi-phase progression designed for your experience level and goals.',
            'estimated_duration_weeks': 6,
            'phases': [
                {
                    'phase_id': 'phase_1',
                    'title': 'Phase 1: Foundations & Core Principles',
                    'description': 'Establish foundational mastery and essential workflows.',
                    'order': 1,
                    'skills': [],
                    'resources': [],
                    'projects': [],
                    'assessment_id': None,
                    'milestone': 'Core competencies established',
                },
                {
                    'phase_id': 'phase_2',
                    'title': 'Phase 2: Applied Projects & Practical Implementation',
                    'description': 'Build realistic projects and integrate advanced techniques.',
                    'order': 2,
                    'skills': [],
                    'resources': [],
                    'projects': [],
                    'assessment_id': None,
                    'milestone': 'Production-level project complete',
                }
            ],
        }
