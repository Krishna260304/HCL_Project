from django.urls import path
from projects.consumers import ProjectConsumer

websocket_urlpatterns = [
    path('ws/projects/', ProjectConsumer.as_asgi()),
]
