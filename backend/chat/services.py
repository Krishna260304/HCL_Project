from typing import Any, Dict, Optional
from bson import ObjectId
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
        conv = None
        if conv_id and conv_id != 'default' and ObjectId.is_valid(conv_id):
            conv = ChatRepository.find_conversation_by_id(conv_id)
            if conv and conv.get('user_id') != str(user_id):
                require_owner_or_admin(user_context, conv['user_id'])

        if not conv:
            user_convs = ChatRepository.find_conversations_by_user(str(user_id))
            if user_convs:
                conv = user_convs[0]
                conv_id = str(conv['_id'])
            else:
                conv_doc = {
                    'user_id': str(user_id),
                    'title': data['message'][:40] + ('...' if len(data['message']) > 40 else ''),
                }
                conv_id = ChatRepository.create_conversation(conv_doc)
                conv = ChatRepository.find_conversation_by_id(conv_id)

        user_msg_doc = {
            'conversation_id': str(conv_id),
            'role': ChatRole.USER,
            'content': data['message'],
            'sources': [],
            'metadata': data.get('context', {}),
        }
        user_msg_id = ChatRepository.save_message(user_msg_doc)

        profile = ProfileRepository.find_by_user_id(user_id) or {}
        raw_verified = profile.get('verified_skills', [])
        clean_verified = []
        if isinstance(raw_verified, list):
            for v in raw_verified:
                if isinstance(v, dict):
                    clean_verified.append({
                        'skill_id': str(v.get('skill_id', '')),
                        'verified_score': float(v.get('verified_score', 0.0))
                    })
                elif isinstance(v, str):
                    clean_verified.append({'skill_id': v, 'verified_score': 70.0})

        learner_context = {
            'user_id': str(user_id),
            'experience_level': profile.get('experience_level', 'beginner'),
            'verified_skills': clean_verified,
            'interests': profile.get('interests', []),
            'current_goal': profile.get('goals', [''])[0] if profile.get('goals') else '',
            'target_outcome': profile.get('target_outcome', ''),
        }

        from ai_integrations.assistant import AssistantClient
        ai_response = AssistantClient.chat(
            user_id=str(user_id),
            conversation_id=str(conv_id),
            message=data['message'],
            learner_context=serialize_mongo_doc(learner_context)
        )

        reply_content = ai_response.get('answer') or ai_response.get('message') or ai_response.get('reply') or 'I am here to guide your learning path.'
        ai_msg_doc = {
            'conversation_id': str(conv_id),
            'role': ChatRole.ASSISTANT,
            'content': reply_content,
            'sources': ai_response.get('sources', []),
            'metadata': ai_response.get('context_metadata', {}),
        }
        ai_msg_id = ChatRepository.save_message(ai_msg_doc)

        return {
            'conversation_id': str(conv_id),
            # Keep a small, stable response field for clients that only need
            # the assistant text. The full message is still returned below.
            'reply': reply_content,
            'user_message': serialize_mongo_doc({**user_msg_doc, '_id': user_msg_id}),
            'assistant_message': serialize_mongo_doc({**ai_msg_doc, '_id': ai_msg_id}),
            'recommended_actions': ai_response.get('recommended_actions', []),
            'sources': ai_response.get('sources', []),
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
        if not conv_id or not ObjectId.is_valid(conv_id):
            user_convs = ChatRepository.find_conversations_by_user(str(auth_user['user_id']))
            if user_convs:
                conv = user_convs[0]
                conv_id = str(conv['_id'])
            else:
                return {'conversation': None, 'messages': []}
        else:
            conv = ChatRepository.find_conversation_by_id(conv_id)
            if not conv:
                return {'conversation': None, 'messages': []}
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
