import pytest
from goals.services import GoalService

def test_goal_lifecycle(learner_account):
    user_context = {
        'user_id': learner_account['user']['id'],
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    created = GoalService.create_goal({
        'title': 'Master Django and Channels Backend Architecture',
        'goal_type': 'career',
        'timeline': '3 months',
    }, user_context)
    assert created['title'] == 'Master Django and Channels Backend Architecture'
    goal_id = created['id']

    listed = GoalService.list_goals({}, user_context)
    assert len(listed['goals']) == 1

    updated = GoalService.update_goal({
        'goal_id': goal_id,
        'status': 'completed',
    }, user_context)
    assert updated['status'] == 'completed'

    deleted = GoalService.delete_goal({'goal_id': goal_id}, user_context)
    assert deleted['deleted'] is True
