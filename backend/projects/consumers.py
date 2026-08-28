from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from projects.services import ProjectService

class ProjectConsumer(BaseAsyncConsumer):
    require_auth = False
    required_role = None

    handlers = {
        'project.list': lambda payload, user: ProjectService.list_projects(payload, user),
        'project.get': lambda payload, user: ProjectService.get_project(payload, user),
    }
