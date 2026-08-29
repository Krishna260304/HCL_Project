from django.urls import path
from assessments.consumers import AssessmentConsumer

websocket_urlpatterns = [
    path('ws/assessments/', AssessmentConsumer.as_asgi()),
]
