from django.urls import path
from progress.consumers import ProgressConsumer

websocket_urlpatterns = [
    path('ws/progress/', ProgressConsumer.as_asgi()),
]
