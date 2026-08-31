import pytest
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import mongomock
from database.mongo import set_mongo_client
from authentication.services import AuthService

@pytest.fixture(autouse=True)
def setup_test_database():
    client = mongomock.MongoClient()
    set_mongo_client(client)
    yield client
    client.close()

@pytest.fixture
def learner_account():
    result = AuthService.register_learner({
        'email': 'learner@test.com',
        'password': 'Password123!',
        'name': 'Test Learner',
    })
    return result

@pytest.fixture
def admin_account():
    result = AuthService.seed_initial_admin()
    login_result = AuthService.login({
        'email': result['email'],
        'password': 'AdminSecurePass123!',
    })
    return login_result
