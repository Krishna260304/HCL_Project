from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from profiles.services import ProfileService

class ProfileConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'profile.get': lambda payload, user: ProfileService.get_profile(payload, user),
        'profile.update': lambda payload, user: ProfileService.update_profile(payload, user),
    }
