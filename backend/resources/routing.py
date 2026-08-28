from django.urls import path
from resources.consumers import ResourceConsumer

websocket_urlpatterns = [
    path('ws/resources/', ResourceConsumer.as_asgi()),
]
