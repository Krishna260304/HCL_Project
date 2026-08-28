from django.urls import path
from authentication.consumers import AuthConsumer
from users.consumers import UserConsumer
from admin_portal.consumers import AdminConsumer
from chat.consumers import ChatConsumer
from notifications.consumers import NotificationConsumer
from core.websocket import UnifiedGatewayConsumer

websocket_urlpatterns = [
    path('ws/auth/', AuthConsumer.as_asgi()),
    path('ws/user/', UserConsumer.as_asgi()),
    path('ws/admin/', AdminConsumer.as_asgi()),
    path('ws/chat/', ChatConsumer.as_asgi()),
    path('ws/notifications/', NotificationConsumer.as_asgi()),
    path('ws/', UnifiedGatewayConsumer.as_asgi()),
]
