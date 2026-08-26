from django.urls import path
from feedback.consumers import FeedbackConsumer

websocket_urlpatterns = [
    path('ws/feedback/', FeedbackConsumer.as_asgi()),
]
