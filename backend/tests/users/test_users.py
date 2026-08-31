import pytest
from users.services import UserService
from core.exceptions import AuthorizationError

def test_user_get_self(learner_account):
    user_context = {
        'user_id': learner_account['user']['id'],
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    self_data = UserService.get_user_self(user_context)
    assert self_data['email'] == learner_account['user']['email']
    assert 'password_hash' not in self_data

def test_admin_list_users(admin_account, learner_account):
    admin_context = {
        'user_id': admin_account['user']['id'],
        'email': admin_account['user']['email'],
        'role': 'admin',
    }
    res = UserService.list_users({}, admin_context)
    assert res['total'] >= 2

def test_learner_cannot_list_users(learner_account):
    learner_context = {
        'user_id': learner_account['user']['id'],
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    with pytest.raises(AuthorizationError):
        UserService.list_users({}, learner_context)
