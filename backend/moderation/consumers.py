from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from moderation.services import ModerationService

class ModerationConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'moderation.flag': lambda payload, user: ModerationService.flag_content(payload, user),
        'moderation.list': lambda payload, user: ModerationService.list_moderation_items(payload, user),
        'moderation.resolve': lambda payload, user: ModerationService.resolve_item(payload, user),
    }
