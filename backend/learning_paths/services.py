from typing import Any, Dict, List, Optional
from core.permissions import require_authenticated, require_admin, require_owner_or_admin
from core.exceptions import NotFoundError, ValidationError
from core.utilities import serialize_mongo_doc, serialize_mongo_list, now_utc
from core.constants import PhaseStatus
from learning_paths.repository import LearningPathRepository
from learning_paths.validators import (
    validate_path_create_payload,
    validate_path_update_payload,
    validate_phase_action_payload,
)
from profiles.repository import ProfileRepository
from goals.repository import GoalRepository

class LearningPathService:
    @classmethod
    def get_learning_path(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        target_user_id = payload.get('user_id', user_id)
        require_owner_or_admin(user_context, target_user_id)

        path_id = payload.get('path_id')
        if path_id:
            path = LearningPathRepository.find_by_id(path_id)
        else:
            path = LearningPathRepository.find_by_user_id(target_user_id, status='active')
            if not path:
                path = LearningPathRepository.find_by_user_id(target_user_id)

        if not path:
            return {'learning_path': None}

        serialized = serialize_mongo_doc(path)
        if not serialized.get('goal'):
            serialized['goal'] = serialized.get('title', 'Your Learning Path')
        if serialized.get('phases'):
            for p in serialized['phases']:
                if 'id' not in p or not p['id']:
                    p['id'] = p.get('phase_id', 'phase')
                if 'estimated_time' not in p or not p['estimated_time']:
                    p['estimated_time'] = '2-3 weeks'
        return {'learning_path': serialized}

    @classmethod
    def generate_learning_path(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        goal_id = payload.get('goal_id')

        profile = ProfileRepository.find_by_user_id(user_id) or {}
        goal = GoalRepository.find_by_id(goal_id) if goal_id else None

        from ai_integrations.learning_path import LearningPathClient
        # The onboarding UI uses target_role while older clients use goal.
        # Normalize both here so the career destination is never discarded.
        target_role = payload.get('target_role') or payload.get('goal') or profile.get('target_outcome') or (profile.get('goals', [None])[0] if profile.get('goals') else None)
        effective_goal = goal.get('title') if goal else (target_role or 'Software Mastery')

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

        input_data = {
            'user_id': str(user_id),
            'goal': effective_goal,
            'experience_level': profile.get('experience_level', 'beginner'),
            'verified_skills': clean_verified,
            'skill_gaps': payload.get('skill_gaps', profile.get('skill_gaps', [])),
            'interests': profile.get('interests', []),
            'available_hours': profile.get('available_hours', 5),
            'timeline': payload.get('timeline') or profile.get('timeline'),
            'learning_preferences': profile.get('learning_preferences', {}),
        }
        generated = LearningPathClient.generate_learning_path(serialize_mongo_doc(input_data))

        raw_phases = generated.get('phases', [])
        formatted_phases = []
        for idx, phase in enumerate(raw_phases):
            phase_id = phase.get('phase_id') or phase.get('id') or f'phase_{idx + 1}'
            phase_status = PhaseStatus.CURRENT if idx == 0 else PhaseStatus.LOCKED
            phase_obj = phase.get('objective') or phase.get('description', '')
            formatted_phases.append({
                'id': str(phase_id),
                'phase_id': str(phase_id),
                'title': phase.get('title', f'Phase {idx + 1}'),
                'description': phase.get('description', ''),
                'objective': phase_obj,
                'order': phase.get('order', idx + 1),
                'skills': phase.get('skills', []),
                'resources': phase.get('resources', []),
                'projects': phase.get('projects', []),
                'assessment': phase.get('assessment') if isinstance(phase.get('assessment'), str) else (phase.get('assessment', {}).get('title') if isinstance(phase.get('assessment'), dict) else None),
                'assessment_id': phase.get('assessment_id') or (phase.get('assessment', {}).get('assessment_id') if isinstance(phase.get('assessment'), dict) else None),
                'milestone': phase.get('milestone', 'Phase milestone reached'),
                'estimated_time': f"{phase.get('estimated_duration_weeks', 2)} weeks" if isinstance(phase.get('estimated_duration_weeks'), (int, float)) else phase.get('estimated_time', '2-3 weeks'),
                'status': phase_status,
                'progress': 0.0,
            })

        duration_val = generated.get('estimated_duration_weeks', 8)
        duration_str = f"{duration_val} weeks" if isinstance(duration_val, (int, float)) else str(duration_val)

        path_doc = {
            'user_id': str(user_id),
            'goal_id': str(goal_id) if goal_id else None,
            'goal': effective_goal,
            'title': generated.get('title', f'Learning Path: {effective_goal}'),
            'description': generated.get('description', 'Custom curated path based on your goals and background.'),
            'duration': duration_str,
            'status': 'active',
            'progress': 0.0,
            'phases': formatted_phases,
        }
        path_id = LearningPathRepository.create_path(path_doc)
        created = LearningPathRepository.find_by_id(path_id)
        return serialize_mongo_doc(created)

    @classmethod
    def update_learning_path(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_authenticated(user_context)
        data = validate_path_update_payload(payload)
        path_id = data['path_id']
        path = LearningPathRepository.find_by_id(path_id)
        if not path:
            raise NotFoundError('Learning path not found.')

        require_owner_or_admin(user_context, path['user_id'])
        LearningPathRepository.update_path(path_id, data['updates'])
        updated = LearningPathRepository.find_by_id(path_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def complete_phase(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        data = validate_phase_action_payload(payload)
        path_id = data['path_id']
        phase_id = data['phase_id']

        path = LearningPathRepository.find_by_id(path_id)
        if not path:
            raise NotFoundError('Learning path not found.')
        require_owner_or_admin(user_context, path['user_id'])

        phases = path.get('phases', [])
        found = False
        completed_count = 0
        total_phases = len(phases)

        for i, phase in enumerate(phases):
            if phase.get('phase_id') == phase_id:
                phase['status'] = PhaseStatus.COMPLETED
                phase['progress'] = 100.0
                found = True
                if i + 1 < total_phases and phases[i + 1].get('status') == PhaseStatus.LOCKED:
                    phases[i + 1]['status'] = PhaseStatus.CURRENT
            if phase.get('status') == PhaseStatus.COMPLETED:
                completed_count += 1

        if not found:
            raise NotFoundError('Phase not found in this learning path.')

        overall_progress = round((completed_count / total_phases) * 100.0, 2) if total_phases > 0 else 0.0
        path_status = 'completed' if completed_count == total_phases else 'active'

        LearningPathRepository.update_path(path_id, {
            'phases': phases,
            'progress': overall_progress,
            'status': path_status,
        })
        updated = LearningPathRepository.find_by_id(path_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def skip_phase(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        data = validate_phase_action_payload(payload)
        path_id = data['path_id']
        phase_id = data['phase_id']

        path = LearningPathRepository.find_by_id(path_id)
        if not path:
            raise NotFoundError('Learning path not found.')
        require_owner_or_admin(user_context, path['user_id'])

        phases = path.get('phases', [])
        found = False
        for i, phase in enumerate(phases):
            if phase.get('phase_id') == phase_id:
                phase['status'] = PhaseStatus.SKIPPED
                found = True
                if i + 1 < len(phases) and phases[i + 1].get('status') == PhaseStatus.LOCKED:
                    phases[i + 1]['status'] = PhaseStatus.CURRENT

        if not found:
            raise NotFoundError('Phase not found in this learning path.')

        LearningPathRepository.update_path(path_id, {'phases': phases})
        updated = LearningPathRepository.find_by_id(path_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def list_all_paths_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        paths = LearningPathRepository.find_all({})
        return {'learning_paths': serialize_mongo_list(paths)}

    @classmethod
    def override_path_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        path_id = payload.get('path_id')
        updates = payload.get('updates', payload)
        LearningPathRepository.update_path(path_id, updates)
        updated = LearningPathRepository.find_by_id(path_id)
        return serialize_mongo_doc(updated)
