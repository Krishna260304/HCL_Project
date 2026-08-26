from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from authentication.services import AuthService

class AuthConsumer(BaseAsyncConsumer):
    require_auth = False
    required_role = None

    handlers = {
        'auth.register': lambda payload, user: AuthService.register_learner(payload),
        'auth.login': lambda payload, user: AuthService.login(payload),
        'auth.refresh': lambda payload, user: AuthService.refresh_token(payload),
        'auth.password_reset_request': lambda payload, user: AuthService.request_password_reset(payload),
        'auth.password_reset_confirm': lambda payload, user: AuthService.confirm_password_reset(payload),
        'auth.change_password': lambda payload, user: AuthService.change_password(payload, user),
        'auth.logout': lambda payload, user: AuthService.logout(payload, user),
    }
