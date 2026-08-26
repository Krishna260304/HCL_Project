from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from analytics.services import AnalyticsService

class AnalyticsConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = 'admin'

    handlers = {
        'analytics.overview': lambda payload, user: AnalyticsService.get_overview(payload, user),
    }
