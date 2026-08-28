from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from feedback.services import FeedbackService

class FeedbackConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'feedback.create': lambda payload, user: FeedbackService.create_feedback(payload, user),
        'feedback.list_self': lambda payload, user: FeedbackService.list_self_feedback(payload, user),
    }
