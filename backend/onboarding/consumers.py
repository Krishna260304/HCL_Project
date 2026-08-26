from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from onboarding.services import OnboardingService

class OnboardingConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'onboarding.get': lambda payload, user: OnboardingService.get_session(user),
        'onboarding.save_step': lambda payload, user: OnboardingService.save_step(payload, user),
        'onboarding.complete': lambda payload, user: OnboardingService.complete_onboarding(payload, user),
        'onboarding.questions': lambda payload, user: OnboardingService.get_questions(user),
    }
