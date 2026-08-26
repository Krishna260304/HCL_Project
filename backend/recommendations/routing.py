from django.urls import path
from recommendations.consumers import RecommendationConsumer

websocket_urlpatterns = [
    path('ws/recommendations/', RecommendationConsumer.as_asgi()),
]
