from typing import Any, Dict, Optional
from core.permissions import require_authenticated, require_owner_or_admin
from core.exceptions import NotFoundError
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from goals.repository import GoalRepository
from goals.validators import validate_create_goal_payload, validate_update_goal_payload

class GoalService:
    @classmethod
    def create_goal(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        data = validate_create_goal_payload(payload)
        user_id = auth_user['user_id']
        data['user_id'] = user_id

        goal_id = GoalRepository.create_goal(data)
        created = GoalRepository.find_by_id(goal_id)
        return serialize_mongo_doc(created)

    @classmethod
    def list_goals(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        target_user_id = payload.get('user_id', user_id)
        require_owner_or_admin(user_context, target_user_id)

        status = payload.get('status')
        goals = GoalRepository.find_by_user_id(target_user_id, status=status)
        return {'goals': serialize_mongo_list(goals)}

    @classmethod
    def get_goal(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_authenticated(user_context)
        goal_id = payload.get('goal_id')
        goal = GoalRepository.find_by_id(goal_id)
        if not goal:
            raise NotFoundError('Goal not found.')

        require_owner_or_admin(user_context, goal['user_id'])
        return serialize_mongo_doc(goal)

    @classmethod
    def update_goal(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_authenticated(user_context)
        data = validate_update_goal_payload(payload)
        goal_id = data['goal_id']
        goal = GoalRepository.find_by_id(goal_id)
        if not goal:
            raise NotFoundError('Goal not found.')

        require_owner_or_admin(user_context, goal['user_id'])
        GoalRepository.update_goal(goal_id, data['updates'])
        updated = GoalRepository.find_by_id(goal_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def delete_goal(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_authenticated(user_context)
        goal_id = payload.get('goal_id')
        goal = GoalRepository.find_by_id(goal_id)
        if not goal:
            raise NotFoundError('Goal not found.')

        require_owner_or_admin(user_context, goal['user_id'])
        GoalRepository.delete_goal(goal_id)
        return {'goal_id': goal_id, 'deleted': True}

    @classmethod
    def analyze_goal_ai(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_authenticated(user_context)
        description = payload.get('description', '')
        from ai_integrations.goal_analysis import GoalAnalysisClient
        analysis = GoalAnalysisClient.analyze_goal(description)
        return analysis
