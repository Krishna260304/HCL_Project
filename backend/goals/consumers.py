from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from goals.services import GoalService

class GoalConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'goal.create': lambda payload, user: GoalService.create_goal(payload, user),
        'goal.list': lambda payload, user: GoalService.list_goals(payload, user),
        'goal.get': lambda payload, user: GoalService.get_goal(payload, user),
        'goal.update': lambda payload, user: GoalService.update_goal(payload, user),
        'goal.delete': lambda payload, user: GoalService.delete_goal(payload, user),
        'goal.analyze': lambda payload, user: GoalService.analyze_goal_ai(payload, user),
    }
