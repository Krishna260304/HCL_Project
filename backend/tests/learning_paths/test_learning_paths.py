import pytest
from learning_paths.services import LearningPathService

def test_learning_path_generation_and_progression(learner_account):
    user_context = {
        'user_id': learner_account['user']['id'],
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    path = LearningPathService.generate_learning_path({'goal': 'Full Stack Backend Architect'}, user_context)
    assert 'phases' in path
    assert len(path['phases']) >= 1
    assert path['phases'][0]['status'] == 'current'

    phase_1_id = path['phases'][0]['phase_id']
    completed = LearningPathService.complete_phase({
        'path_id': path['id'],
        'phase_id': phase_1_id,
    }, user_context)
    assert completed['phases'][0]['status'] == 'completed'
