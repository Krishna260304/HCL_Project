from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from learning_paths.services import LearningPathService

class LearningPathConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'learning_path.get': lambda payload, user: LearningPathService.get_learning_path(payload, user),
        'learning_path.generate': lambda payload, user: LearningPathService.generate_learning_path(payload, user),
        'learning_path.update': lambda payload, user: LearningPathService.update_learning_path(payload, user),
        'learning_path.phase.complete': lambda payload, user: LearningPathService.complete_phase(payload, user),
        'learning_path.phase.skip': lambda payload, user: LearningPathService.skip_phase(payload, user),
    }
