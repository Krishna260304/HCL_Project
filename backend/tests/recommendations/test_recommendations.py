import pytest
from recommendations.services import RecommendationService

def test_recommendations_list_and_update(learner_account):
    user_context = {
        'user_id': learner_account['user']['id'],
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    recs = RecommendationService.list_recommendations({}, user_context)
    assert 'recommendations' in recs
