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
        return {'learning_path': serialize_mongo_doc(path)}

    @classmethod
    def generate_learning_path(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        goal_id = payload.get('goal_id')

        profile = ProfileRepository.find_by_user_id(user_id) or {}
        goal = GoalRepository.find_by_id(goal_id) if goal_id else None

        from ai_integrations.learning_path import LearningPathClient
        input_data = {
            'user_id': str(user_id),
            'goal': goal.get('title') if goal else payload.get('goal', 'Software Mastery'),
            'experience_level': profile.get('experience_level', 'beginner'),
            'verified_skills': profile.get('verified_skills', []),
            'interests': profile.get('interests', []),
            'available_hours': profile.get('available_hours', 5),
            'learning_preferences': profile.get('learning_preferences', {}),
        }
        generated = LearningPathClient.generate_learning_path(input_data)

        raw_phases = generated.get('phases', [])
        formatted_phases = []
        for idx, phase in enumerate(raw_phases):
            phase_status = PhaseStatus.CURRENT if idx == 0 else PhaseStatus.LOCKED
            formatted_phases.append({
                'phase_id': phase.get('phase_id', f'phase_{idx + 1}'),
                'title': phase.get('title', f'Phase {idx + 1}'),
                'description': phase.get('description', ''),
                'order': idx + 1,
                'skills': phase.get('skills', []),
                'resources': phase.get('resources', []),
                'projects': phase.get('projects', []),
                'assessment_id': phase.get('assessment_id'),
                'milestone': phase.get('milestone', ''),
                'status': phase_status,
                'progress': 0.0,
            })

        path_doc = {
            'user_id': str(user_id),
            'goal_id': str(goal_id) if goal_id else None,
            'title': generated.get('title', 'Personalized Learning Roadmap'),
            'description': generated.get('description', 'Custom curated path based on your goals and background.'),
            'duration': generated.get('estimated_duration_weeks', 8),
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
