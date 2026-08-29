from django.urls import path
from external_resources.consumers import ExternalResourceConsumer

websocket_urlpatterns = [
    path('ws/external_resources/', ExternalResourceConsumer.as_asgi()),
]
