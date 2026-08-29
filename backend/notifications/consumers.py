from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from notifications.services import NotificationService

class NotificationConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'notification.list': lambda payload, user: NotificationService.list_notifications(payload, user),
        'notification.mark_read': lambda payload, user: NotificationService.mark_as_read(payload, user),
        'notification.mark_all_read': lambda payload, user: NotificationService.mark_all_as_read(payload, user),
    }
