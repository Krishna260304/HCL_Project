from django.urls import path
from authentication.consumers import AuthConsumer

websocket_urlpatterns = [
    path('ws/auth/', AuthConsumer.as_asgi()),
]
