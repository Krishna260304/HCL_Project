import pytest
from progress.services import ProgressService
from learning_paths.services import LearningPathService

def test_progress_tracking(learner_account):
    user_context = {
        'user_id': learner_account['user']['id'],
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    path = LearningPathService.generate_learning_path({'goal': 'DevOps'}, user_context)
    prog = ProgressService.update_progress({
        'learning_path_id': path['id'],
        'phase_id': 'phase_1',
        'progress_percentage': 50.0,
        'time_spent': 120,
    }, user_context)
    assert prog['progress_percentage'] == 50.0

    act = ProgressService.get_activity({}, user_context)
    assert len(act['activity']) >= 1
