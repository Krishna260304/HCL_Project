import pytest
from core.websocket import UnifiedGatewayConsumer
from authentication.services import AuthService

def test_unified_gateway_dispatch():
    consumer = UnifiedGatewayConsumer()
    handler = consumer.get_handler('auth.register')
    assert handler is not None

    res = handler({
        'email': 'gateway_test@example.com',
        'password': 'Password123!',
        'name': 'Gateway Test User',
    }, None)
    assert res['user']['email'] == 'gateway_test@example.com'
    assert 'tokens' in res
