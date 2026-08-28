from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from skills.services import SkillService

class SkillConsumer(BaseAsyncConsumer):
    require_auth = False
    required_role = None

    handlers = {
        'skill.list': lambda payload, user: SkillService.list_skills(payload, user),
        'skill.get': lambda payload, user: SkillService.get_skill(payload, user),
        'skill.graph': lambda payload, user: SkillService.get_skill_graph(payload, user),
        'skill.prerequisites': lambda payload, user: SkillService.get_prerequisites(payload, user),
        'skill.dependents': lambda payload, user: SkillService.get_dependents(payload, user),
    }
