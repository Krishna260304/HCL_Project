import pytest
from notifications.services import NotificationService

def test_notification_flow(learner_account):
    user_id = learner_account['user']['id']
    user_context = {
        'user_id': user_id,
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    notif = NotificationService.create_and_send({
        'user_id': user_id,
        'title': 'Welcome!',
        'message': 'Welcome to LearnPath AI.',
        'type': 'system',
    })
    assert notif['title'] == 'Welcome!'

    listed = NotificationService.list_notifications({}, user_context)
    assert len(listed['notifications']) == 1

    NotificationService.mark_all_as_read({}, user_context)
    unread = NotificationService.list_notifications({'unread_only': True}, user_context)
    assert len(unread['notifications']) == 0
