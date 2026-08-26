from django.urls import path
from analytics.consumers import AnalyticsConsumer

websocket_urlpatterns = [
    path('ws/analytics/', AnalyticsConsumer.as_asgi()),
]
