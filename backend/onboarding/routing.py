from django.urls import path
from onboarding.consumers import OnboardingConsumer

websocket_urlpatterns = [
    path('ws/onboarding/', OnboardingConsumer.as_asgi()),
]
