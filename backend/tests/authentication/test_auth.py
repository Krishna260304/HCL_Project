import pytest
from authentication.services import AuthService
from core.exceptions import AuthenticationError, ConflictError

def test_learner_registration_and_login():
    reg_data = {
        'email': 'newlearner@example.com',
        'password': 'SecurePassword123!',
        'name': 'New Learner',
    }
    reg_res = AuthService.register_learner(reg_data)
    assert reg_res['user']['email'] == 'newlearner@example.com'
    assert 'access_token' in reg_res['tokens']

    login_res = AuthService.login({
        'email': 'newlearner@example.com',
        'password': 'SecurePassword123!',
    })
    assert login_res['user']['role'] == 'learner'
    assert 'access_token' in login_res['tokens']

def test_duplicate_registration_fails():
    reg_data = {
        'email': 'duplicate@example.com',
        'password': 'SecurePassword123!',
        'name': 'Dup Learner',
    }
    AuthService.register_learner(reg_data)
    with pytest.raises(ConflictError):
        AuthService.register_learner(reg_data)

def test_invalid_login_fails():
    with pytest.raises(AuthenticationError):
        AuthService.login({
            'email': 'nonexistent@example.com',
            'password': 'WrongPassword123!',
        })
