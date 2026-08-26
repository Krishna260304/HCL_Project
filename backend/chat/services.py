from typing import Any, Dict, Optional
from core.permissions import require_authenticated, require_owner_or_admin
from core.exceptions import NotFoundError, ValidationError
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from core.constants import ChatRole
from chat.repository import ChatRepository
from chat.validators import validate_chat_send_payload, validate_create_conversation_payload
from profiles.repository import ProfileRepository

class ChatService:
    @classmethod
    def send_message(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        data = validate_chat_send_payload(payload)

        conv_id = data.get('conversation_id')
        if not conv_id:
            conv_doc = {
                'user_id': str(user_id),
                'title': data['message'][:40] + ('...' if len(data['message']) > 40 else ''),
            }
            conv_id = ChatRepository.create_conversation(conv_doc)
        else:
            conv = ChatRepository.find_conversation_by_id(conv_id)
            if not conv:
                raise NotFoundError('Conversation not found.')
            require_owner_or_admin(user_context, conv['user_id'])

        user_msg_doc = {
            'conversation_id': str(conv_id),
            'role': ChatRole.USER,
            'content': data['message'],
            'sources': [],
            'metadata': data.get('context', {}),
        }
        user_msg_id = ChatRepository.save_message(user_msg_doc)

        profile = ProfileRepository.find_by_user_id(user_id) or {}
        learner_context = {
            'user_id': str(user_id),
            'experience_level': profile.get('experience_level', 'beginner'),
            'verified_skills': profile.get('verified_skills', []),
            'interests': profile.get('interests', []),
        }

        from ai_integrations.assistant import AssistantClient
        ai_response = AssistantClient.chat(
            user_id=str(user_id),
            conversation_id=str(conv_id),
            message=data['message'],
            learner_context=learner_context
        )

        ai_msg_doc = {
            'conversation_id': str(conv_id),
            'role': ChatRole.ASSISTANT,
            'content': ai_response.get('answer', ai_response.get('message', 'I am here to guide your learning path.')),
            'sources': ai_response.get('sources', []),
            'metadata': ai_response.get('context_metadata', {}),
        }
        ai_msg_id = ChatRepository.save_message(ai_msg_doc)

        return {
            'conversation_id': str(conv_id),
            'user_message': serialize_mongo_doc({**user_msg_doc, '_id': user_msg_id}),
            'assistant_message': serialize_mongo_doc({**ai_msg_doc, '_id': ai_msg_id}),
            'recommended_actions': ai_response.get('recommended_actions', []),
        }

    @classmethod
    def list_conversations(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        convs = ChatRepository.find_conversations_by_user(auth_user['user_id'])
        return {'conversations': serialize_mongo_list(convs)}

    @classmethod
    def get_conversation_history(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        conv_id = payload.get('conversation_id')
        conv = ChatRepository.find_conversation_by_id(conv_id)
        if not conv:
            raise NotFoundError('Conversation not found.')

        require_owner_or_admin(user_context, conv['user_id'])
        messages = ChatRepository.find_messages_by_conversation(conv_id)
        return {
            'conversation': serialize_mongo_doc(conv),
            'messages': serialize_mongo_list(messages),
        }

    @classmethod
    def create_conversation(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        data = validate_create_conversation_payload(payload)
        doc = {
            'user_id': str(auth_user['user_id']),
            'title': data['title'],
            'metadata': data['metadata'],
        }
        conv_id = ChatRepository.create_conversation(doc)
        created = ChatRepository.find_conversation_by_id(conv_id)
        return serialize_mongo_doc(created)
