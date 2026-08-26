from typing import Any, Dict
from ai_integrations.rag import RAGClient

class AssistantClient:
    @classmethod
    def chat(
        cls,
        user_id: str,
        conversation_id: str,
        message: str,
        learner_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        return RAGClient.query(
            user_id=user_id,
            conversation_id=conversation_id,
            message=message,
            learner_context=learner_context
        )
