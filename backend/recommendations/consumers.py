from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from recommendations.services import RecommendationService

class RecommendationConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'recommendation.list': lambda payload, user: RecommendationService.list_recommendations(payload, user),
        'recommendation.update_status': lambda payload, user: RecommendationService.update_status(payload, user),
    }
