from django.urls import path
from skills.consumers import SkillConsumer

websocket_urlpatterns = [
    path('ws/skills/', SkillConsumer.as_asgi()),
]
