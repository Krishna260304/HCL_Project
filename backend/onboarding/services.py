from typing import Any, Dict, List, Optional
from core.permissions import require_authenticated, require_admin
from core.exceptions import NotFoundError
from core.utilities import serialize_mongo_doc, serialize_mongo_list, now_utc
from onboarding.repository import OnboardingRepository
from onboarding.validators import (
    validate_save_step_payload,
    validate_question_create_payload,
    validate_question_update_payload
)
from profiles.repository import ProfileRepository

class OnboardingService:
    @classmethod
    def get_session(cls, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        session = OnboardingRepository.find_session_by_user_id(user_id)
        if not session:
            session_doc = {
                'user_id': user_id,
                'current_step': 1,
                'completed_steps': [],
                'answers': {},
                'status': 'in_progress',
                'completed_at': None,
            }
            session_id = OnboardingRepository.create_session(session_doc)
            session = OnboardingRepository.find_session_by_user_id(user_id)
        return serialize_mongo_doc(session)

    @classmethod
    def save_step(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        data = validate_save_step_payload(payload)
        step = data['step']
        step_answers = data['answers']

        session = OnboardingRepository.find_session_by_user_id(user_id)
        current_answers = session.get('answers', {}) if session else {}
        completed_steps = session.get('completed_steps', []) if session else []

        current_answers.update(step_answers)
        if step not in completed_steps:
            completed_steps.append(step)

        updates = {
            'current_step': step + 1,
            'completed_steps': completed_steps,
            'answers': current_answers,
            'status': 'in_progress',
        }
        OnboardingRepository.update_session(user_id, updates)
        updated_session = OnboardingRepository.find_session_by_user_id(user_id)
        return serialize_mongo_doc(updated_session)

    @classmethod
    def complete_onboarding(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']

        final_answers = payload.get('answers', {})
        session = OnboardingRepository.find_session_by_user_id(user_id)
        all_answers = session.get('answers', {}) if session else {}
        all_answers.update(final_answers)

        updates = {
            'status': 'completed',
            'answers': all_answers,
            'completed_at': now_utc(),
        }
        OnboardingRepository.update_session(user_id, updates)

        profile_updates: Dict[str, Any] = {}
        fields_to_copy = [
            'name', 'education', 'academic_background', 'current_status', 'current_role',
            'experience_years', 'experience_level', 'goals', 'interests', 'knowledge_areas',
            'learning_preferences', 'learning_constraints', 'motivation', 'target_outcome',
            'timeline', 'available_hours', 'practical_experience', 'self_reported_skills'
        ]
        for field in fields_to_copy:
            if field in all_answers and all_answers[field] is not None:
                profile_updates[field] = all_answers[field]

        if profile_updates:
            ProfileRepository.update_by_user_id(user_id, profile_updates)

        return {'completed': True, 'user_id': user_id, 'profile_updated': bool(profile_updates)}

    @classmethod
    def get_questions(cls, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        questions = OnboardingRepository.list_questions(enabled_only=True)
        return {'questions': serialize_mongo_list(questions)}

    @classmethod
    def list_all_questions_admin(cls, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        questions = OnboardingRepository.list_questions(enabled_only=False)
        return {'questions': serialize_mongo_list(questions)}

    @classmethod
    def create_question_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_question_create_payload(payload)
        q_id = OnboardingRepository.create_question(data)
        created = OnboardingRepository.find_question_by_id(q_id)
        return serialize_mongo_doc(created)

    @classmethod
    def update_question_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_question_update_payload(payload)
        q_id = data['question_id']
        OnboardingRepository.update_question(q_id, data['updates'])
        updated = OnboardingRepository.find_question_by_id(q_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def delete_question_admin(cls, question_id: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        OnboardingRepository.delete_question(question_id)
        return {'question_id': question_id, 'deleted': True}
