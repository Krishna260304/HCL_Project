from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from external_resources.services import ExternalResourceService

class ExternalResourceConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'external_resource.search': lambda payload, user: ExternalResourceService.search_external(payload, user),
    }
