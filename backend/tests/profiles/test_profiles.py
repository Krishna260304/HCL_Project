import pytest
from profiles.services import ProfileService

def test_get_and_update_profile(learner_account):
    user_context = {
        'user_id': learner_account['user']['id'],
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    profile = ProfileService.get_profile({}, user_context)
    assert profile['user_id'] == learner_account['user']['id']

    updated = ProfileService.update_profile({
        'experience_level': 'intermediate',
        'available_hours': 15,
        'interests': ['AI', 'Python', 'WebSockets'],
    }, user_context)
    assert updated['experience_level'] == 'intermediate'
    assert updated['available_hours'] == 15
    assert 'AI' in updated['interests']
