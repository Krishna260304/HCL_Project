from django.urls import path
from platform_settings.consumers import PlatformSettingsConsumer

websocket_urlpatterns = [
    path('ws/settings/', PlatformSettingsConsumer.as_asgi()),
]
