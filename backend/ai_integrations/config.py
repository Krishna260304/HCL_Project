import os
from django.conf import settings

class AIConfig:
    @staticmethod
    def get_base_url() -> str:
        return getattr(settings, 'AI_SERVICE_BASE_URL', os.getenv('AI_SERVICE_BASE_URL', 'https://api.learnpath.ai/v1/ai'))

    @staticmethod
    def get_api_key() -> str:
        return getattr(settings, 'AI_SERVICE_API_KEY', os.getenv('AI_SERVICE_API_KEY', 'ai-key'))

    @staticmethod
    def get_timeout() -> int:
        return getattr(settings, 'AI_SERVICE_TIMEOUT', int(os.getenv('AI_SERVICE_TIMEOUT', '30')))
