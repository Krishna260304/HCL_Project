import pytest
from onboarding.services import OnboardingService

def test_onboarding_step_and_completion(learner_account):
    user_context = {
        'user_id': learner_account['user']['id'],
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    session = OnboardingService.get_session(user_context)
    assert session['current_step'] == 1

    saved = OnboardingService.save_step({
        'step': 1,
        'answers': {'experience_level': 'intermediate', 'available_hours': 10},
    }, user_context)
    assert saved['current_step'] == 2

    completed = OnboardingService.complete_onboarding({
        'answers': {'goals': ['Backend Engineer']},
    }, user_context)
    assert completed['completed'] is True
