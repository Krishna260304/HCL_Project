from django.urls import path
from goals.consumers import GoalConsumer

websocket_urlpatterns = [
    path('ws/goal/', GoalConsumer.as_asgi()),
]
