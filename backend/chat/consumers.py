from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from chat.services import ChatService

class ChatConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'chat.send': lambda payload, user: ChatService.send_message(payload, user),
        'chat.conversations': lambda payload, user: ChatService.list_conversations(payload, user),
        'chat.history': lambda payload, user: ChatService.get_conversation_history(payload, user),
        'chat.create_conversation': lambda payload, user: ChatService.create_conversation(payload, user),
    }
