from typing import Any, Dict
from ai_integrations.client import BaseAIClient
from ai_integrations.exceptions import ExternalAIServiceUnavailableError

class RAGClient:
    endpoint = 'rag/query'

    @classmethod
    def query(
        cls,
        user_id: str,
        conversation_id: str,
        message: str,
        learner_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        payload = {
            'user_id': user_id,
            'conversation_id': conversation_id,
            'message': message,
            'learner_context': learner_context,
        }
        try:
            raw_response = BaseAIClient.post(cls.endpoint, payload)
            return cls.normalize_response(raw_response)
        except ExternalAIServiceUnavailableError:
            return cls.fallback_response(message)

    @classmethod
    def normalize_response(cls, response: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'answer': response.get('answer', ''),
            'sources': response.get('sources', []),
            'context_metadata': response.get('context_metadata', {}),
            'recommended_actions': response.get('recommended_actions', []),
        }

    @classmethod
    def fallback_response(cls, message: str) -> Dict[str, Any]:
        return {
            'answer': f'I am your LearnPath AI Tutor. How can I help you reach your goals regarding: "{message}"?',
            'sources': [],
            'context_metadata': {'mode': 'fallback'},
            'recommended_actions': ['Explore recommended resources', 'Take diagnostic assessment'],
        }
