from django.urls import path
from profiles.consumers import ProfileConsumer

websocket_urlpatterns = [
    path('ws/profile/', ProfileConsumer.as_asgi()),
]
