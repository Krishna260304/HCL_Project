from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from platform_settings.services import PlatformSettingsService

class PlatformSettingsConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = 'admin'

    handlers = {
        'admin.settings.get': lambda payload, user: PlatformSettingsService.get_settings(user),
        'admin.settings.update': lambda payload, user: PlatformSettingsService.update_settings(payload, user),
        'admin.feature_flags.list': lambda payload, user: PlatformSettingsService.list_feature_flags(user),
        'admin.feature_flags.update': lambda payload, user: PlatformSettingsService.update_feature_flag(payload, user),
    }
