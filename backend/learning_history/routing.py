from django.urls import path
from learning_history.consumers import LearningHistoryConsumer

websocket_urlpatterns = [
    path('ws/learning_history/', LearningHistoryConsumer.as_asgi()),
]
