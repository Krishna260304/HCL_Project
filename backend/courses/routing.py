from django.urls import path
from courses.consumers import CourseConsumer

websocket_urlpatterns = [
    path('ws/courses/', CourseConsumer.as_asgi()),
]
