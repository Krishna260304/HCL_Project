from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from learning_history.services import LearningHistoryService

class LearningHistoryConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'learning_history.create': lambda payload, user: LearningHistoryService.create_entry(payload, user),
        'learning_history.list': lambda payload, user: LearningHistoryService.list_entries(payload, user),
        'learning_history.get': lambda payload, user: LearningHistoryService.get_entry(payload, user),
        'learning_history.update': lambda payload, user: LearningHistoryService.update_entry(payload, user),
        'learning_history.delete': lambda payload, user: LearningHistoryService.delete_entry(payload, user),
    }
