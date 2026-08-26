from django.urls import path
from learning_paths.consumers import LearningPathConsumer

websocket_urlpatterns = [
    path('ws/learning_paths/', LearningPathConsumer.as_asgi()),
]
