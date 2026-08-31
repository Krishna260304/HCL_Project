import pytest
from chat.services import ChatService

def test_chat_flow(learner_account):
    user_context = {
        'user_id': learner_account['user']['id'],
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    msg_res = ChatService.send_message({'message': 'How should I structure my backend study schedule?'}, user_context)
    assert 'conversation_id' in msg_res
    assert 'assistant_message' in msg_res

    history = ChatService.get_conversation_history({'conversation_id': msg_res['conversation_id']}, user_context)
    assert len(history['messages']) == 2
