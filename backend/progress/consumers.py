from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from progress.services import ProgressService

class ProgressConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'progress.get': lambda payload, user: ProgressService.get_progress(payload, user),
        'progress.update': lambda payload, user: ProgressService.update_progress(payload, user),
        'progress.skills': lambda payload, user: ProgressService.get_skill_progress(payload, user),
        'progress.activity': lambda payload, user: ProgressService.get_activity(payload, user),
    }
