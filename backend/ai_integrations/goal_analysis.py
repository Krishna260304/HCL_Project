from typing import Any, Dict
from ai_integrations.client import BaseAIClient
from ai_integrations.exceptions import ExternalAIServiceUnavailableError

class GoalAnalysisClient:
    endpoint = 'goal-analysis'

    @classmethod
    def analyze_goal(cls, description: str) -> Dict[str, Any]:
        payload = {'description': description}
        try:
            raw_response = BaseAIClient.post(cls.endpoint, payload, timeout=60)
            return cls.normalize_response(raw_response, description)
        except Exception:
            return cls.fallback_response(description)

    @classmethod
    def normalize_response(cls, response: Dict[str, Any], raw_description: str) -> Dict[str, Any]:
        goal = response.get('goal', raw_description)
        required_skills = response.get('required_skills') or []
        possible_roles = response.get('possible_roles') or []
        return {
            'goal': goal,
            'goal_type': response.get('goal_type', 'career_advancement'),
            'target_outcome': response.get('target_outcome', 'Full proficiency'),
            'timeline': response.get('timeline', '3-6 months'),
            'required_skills': required_skills,
            'recommended_domains': response.get('recommended_domains', []),
            # Stable UI-facing aliases used by the onboarding analyzer.
            'target_role': response.get('target_role') or (possible_roles[0] if possible_roles else goal),
            'extracted_skills': response.get('extracted_skills') or required_skills,
            'summary': response.get('summary') or (
                f"{goal} mapped to a focused curriculum with {len(required_skills)} recommended skills."
            ),
        }

    @classmethod
    def fallback_response(cls, description: str) -> Dict[str, Any]:
        text = description.lower()
        if any(term in text for term in ('ai', 'machine learning', 'data scientist', 'deep learning')):
            skills = ['Python', 'Machine Learning', 'Deep Learning', 'Model Deployment']
        elif any(term in text for term in ('web', 'frontend', 'backend', 'full stack', 'full-stack')):
            skills = ['JavaScript', 'Web Development', 'API Design', 'Databases']
        elif any(term in text for term in ('devops', 'cloud', 'infrastructure')):
            skills = ['Linux', 'Docker', 'Cloud Architecture', 'CI/CD']
        else:
            skills = ['Programming Fundamentals', 'Data Structures', 'Problem Solving']

        return {
            'goal': description,
            'goal_type': 'general_learning',
            'target_outcome': 'Competence and practical application',
            'timeline': '3 months',
            'required_skills': skills,
            'recommended_domains': skills[:2],
            'target_role': description,
            'extracted_skills': skills,
            'summary': f"{description} mapped to a focused curriculum covering {', '.join(skills)}.",
        }
