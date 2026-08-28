from django.urls import path
from moderation.consumers import ModerationConsumer

websocket_urlpatterns = [
    path('ws/moderation/', ModerationConsumer.as_asgi()),
]
