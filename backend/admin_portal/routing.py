from django.urls import path
from admin_portal.consumers import AdminConsumer

websocket_urlpatterns = [
    path('ws/admin/', AdminConsumer.as_asgi()),
]
