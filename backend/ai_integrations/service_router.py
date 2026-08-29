from typing import Any, Dict
from ai_integrations.goal_analysis import GoalAnalysisClient
from ai_integrations.assessment_generation import AssessmentGenerationClient
from ai_integrations.skill_analysis import SkillAnalysisClient
from ai_integrations.resource_analysis import ResourceAnalysisClient
from ai_integrations.recommendation import RecommendationClient
from ai_integrations.learning_path import LearningPathClient
from ai_integrations.rag import RAGClient
from ai_integrations.assistant import AssistantClient
from ai_integrations.adaptive_learning import AdaptiveLearningClient

class AIServiceRouter:
    SERVICES = {
        'goal_analysis': GoalAnalysisClient,
        'assessment_generation': AssessmentGenerationClient,
        'skill_analysis': SkillAnalysisClient,
        'resource_analysis': ResourceAnalysisClient,
        'recommendation': RecommendationClient,
        'learning_path': LearningPathClient,
        'rag': RAGClient,
        'assistant': AssistantClient,
        'adaptive_learning': AdaptiveLearningClient,
    }

    @classmethod
    def get_service(cls, service_name: str) -> Any:
        return cls.SERVICES.get(service_name)
