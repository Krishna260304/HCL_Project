from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from resources.services import ResourceService

class ResourceConsumer(BaseAsyncConsumer):
    require_auth = False
    required_role = None

    handlers = {
        'resource.search': lambda payload, user: ResourceService.search_resources(payload, user),
        'resource.get': lambda payload, user: ResourceService.get_resource(payload, user),
        'resource.list': lambda payload, user: ResourceService.list_resources(payload, user),
    }
