import pytest
from feedback.services import FeedbackService

def test_feedback_flow(learner_account):
    user_context = {
        'user_id': learner_account['user']['id'],
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    fb = FeedbackService.create_feedback({
        'type': 'resource',
        'rating': 5,
        'comment': 'Exceptional content and clarity!',
    }, user_context)
    assert fb['created'] is True

    self_fb = FeedbackService.list_self_feedback({}, user_context)
    assert len(self_fb['feedback']) == 1
