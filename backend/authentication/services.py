from typing import Any, Dict, Optional
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
from core.constants import Roles, UserStatus
from core.exceptions import AuthenticationError, ConflictError, NotFoundError, ValidationError
from core.utilities import serialize_mongo_doc, now_utc
from authentication.repository import AuthRepository
from authentication.tokens import generate_token_pair, verify_token, generate_access_token
from authentication.validators import (
    validate_register_payload,
    validate_login_payload,
    validate_refresh_payload,
    validate_password_reset_request_payload,
    validate_password_reset_confirm_payload,
    validate_change_password_payload,
)

class AuthService:
    @classmethod
    def register_learner(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = validate_register_payload(payload)
        email = data['email']
        existing = AuthRepository.find_by_email(email)
        if existing:
            raise ConflictError('An account with this email address already exists.')

        password_hash = make_password(data['password'])
        user_doc = {
            'email': email,
            'password_hash': password_hash,
            'role': Roles.LEARNER,
            'status': UserStatus.ACTIVE,
            'email_verified': False,
            'profile_id': None,
            'preferences': {
                'language': data.get('language', 'en'),
                'notifications_enabled': True,
                'theme': 'dark',
            },
            'security': {
                'password_changed_at': now_utc(),
            },
            'metadata': {},
        }
        user_id = AuthRepository.create_user(user_doc)

        from profiles.repository import ProfileRepository
        profile_doc = {
            'user_id': user_id,
            'name': data['name'],
            'age_range': data.get('age_range'),
            'country': data.get('country'),
            'language': data.get('language', 'en'),
            'education': None,
            'academic_background': None,
            'current_status': None,
            'current_role': data.get('current_role') or None,
            'experience_years': 0,
            'experience_level': data.get('experience_level', 'beginner'),
            'goals': [data['target_outcome']] if data.get('target_outcome') else [],
            'interests': [],
            'knowledge_areas': [],
            'learning_preferences': {},
            'learning_constraints': {},
            'motivation': None,
            'target_outcome': data.get('target_outcome') or None,
            'timeline': None,
            'available_hours': 5,
            'learning_history': [],
            'practical_experience': [],
            'self_reported_skills': [],
            'verified_skills': [],
        }
        profile_id = ProfileRepository.create_profile(profile_doc)
        AuthRepository.update_profile_id(user_id, profile_id)

        from onboarding.repository import OnboardingRepository
        onboarding_doc = {
            'user_id': user_id,
            'current_step': 1,
            'completed_steps': [],
            'answers': {},
            'status': 'in_progress',
            'started_at': now_utc(),
            'completed_at': None,
        }
        OnboardingRepository.create_session(onboarding_doc)

        tokens = generate_token_pair(user_id, email, Roles.LEARNER)
        return {
            'user': {
                'id': user_id,
                'email': email,
                'role': Roles.LEARNER,
                'status': UserStatus.ACTIVE,
                'profile_id': profile_id,
            },
            'tokens': tokens,
        }

    @classmethod
    def login(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = validate_login_payload(payload)
        email = data['email']
        password = data['password']

        user = AuthRepository.find_by_email(email)
        if not user:
            raise AuthenticationError('Invalid email or password.')

        if not check_password(password, user.get('password_hash', '')):
            raise AuthenticationError('Invalid email or password.')

        status = user.get('status', UserStatus.ACTIVE)
        if status == UserStatus.SUSPENDED:
            raise AuthenticationError('Your account has been suspended. Please contact support.')
        if status == UserStatus.INACTIVE:
            raise AuthenticationError('Your account is inactive.')

        user_id = str(user['_id'])
        role = user.get('role', Roles.LEARNER)
        AuthRepository.update_last_login(user_id)
        tokens = generate_token_pair(user_id, email, role)

        return {
            'user': {
                'id': user_id,
                'email': email,
                'role': role,
                'status': status,
                'profile_id': user.get('profile_id'),
            },
            'tokens': tokens,
        }

    @classmethod
    def refresh_token(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = validate_refresh_payload(payload)
        refresh_token = data['refresh_token']
        token_payload = verify_token(refresh_token, expected_type='refresh')

        user_id = token_payload.get('user_id')
        user = AuthRepository.find_by_id(user_id)
        if not user or user.get('status') != UserStatus.ACTIVE:
            raise AuthenticationError('User account is invalid or no longer active.')

        email = user.get('email')
        role = user.get('role', Roles.LEARNER)
        new_access_token = generate_access_token(user_id, email, role)
        return {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': getattr(settings, 'JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 60) * 60,
        }

    @classmethod
    def request_password_reset(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = validate_password_reset_request_payload(payload)
        user = AuthRepository.find_by_email(data['email'])
        if not user:
            return {'message': 'If the email exists in our system, a password reset token has been generated.'}

        user_id = str(user['_id'])
        reset_token = generate_access_token(user_id, user['email'], user.get('role', Roles.LEARNER))
        return {
            'message': 'If the email exists in our system, a password reset token has been generated.',
            'reset_token': reset_token,
        }

    @classmethod
    def confirm_password_reset(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = validate_password_reset_confirm_payload(payload)
        token_payload = verify_token(data['token'], expected_type='access')
        user_id = token_payload.get('user_id')
        user = AuthRepository.find_by_id(user_id)
        if not user:
            raise NotFoundError('User not found.')

        password_hash = make_password(data['new_password'])
        AuthRepository.update_password_hash(user_id, password_hash)
        return {'message': 'Password has been successfully reset.'}

    @classmethod
    def change_password(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not user_context or not user_context.get('user_id'):
            raise AuthenticationError('Authentication required.')
        data = validate_change_password_payload(payload)
        user_id = user_context['user_id']
        user = AuthRepository.find_by_id(user_id)
        if not user:
            raise NotFoundError('User not found.')

        if not check_password(data['current_password'], user.get('password_hash', '')):
            raise ValidationError('Current password is incorrect.')

        password_hash = make_password(data['new_password'])
        AuthRepository.update_password_hash(user_id, password_hash)
        return {'message': 'Password changed successfully.'}

    @classmethod
    def logout(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'message': 'Logged out successfully.'}

    @classmethod
    def seed_initial_admin(cls) -> Dict[str, Any]:
        admin_email = getattr(settings, 'ADMIN_INITIAL_EMAIL', 'admin@learnpath.ai')
        admin_password = getattr(settings, 'ADMIN_INITIAL_PASSWORD', 'AdminSecurePass123!')
        admin_name = getattr(settings, 'ADMIN_INITIAL_NAME', 'System Administrator')

        existing = AuthRepository.find_by_email(admin_email)
        if existing:
            return {'status': 'exists', 'admin_id': str(existing['_id']), 'email': admin_email}

        password_hash = make_password(admin_password)
        admin_doc = {
            'email': admin_email.lower(),
            'password_hash': password_hash,
            'role': Roles.ADMIN,
            'status': UserStatus.ACTIVE,
            'email_verified': True,
            'profile_id': None,
            'preferences': {'theme': 'dark', 'notifications_enabled': True},
            'security': {'password_changed_at': now_utc()},
            'metadata': {'seeded': True},
        }
        admin_id = AuthRepository.create_user(admin_doc)
        return {'status': 'created', 'admin_id': admin_id, 'email': admin_email}
