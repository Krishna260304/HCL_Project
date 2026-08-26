from typing import Any, Dict, List, Optional
from core.permissions import require_authenticated, require_admin, require_owner_or_admin
from core.exceptions import NotFoundError, ValidationError
from core.utilities import serialize_mongo_doc, serialize_mongo_list, now_utc
from core.constants import ExperienceLevel, AttemptStatus, EventNames
from assessments.repository import AssessmentRepository
from assessments.scoring import DeterministicScoringEngine
from assessments.validators import (
    validate_assessment_create_payload,
    validate_assessment_update_payload,
    validate_assessment_question_create_payload,
    validate_submit_attempt_payload,
)
from profiles.repository import ProfileRepository
from progress.repository import ProgressRepository

class AssessmentService:
    @classmethod
    def get_assessment_requirement(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        profile = ProfileRepository.find_by_user_id(user_id)
        exp_level = profile.get('experience_level', ExperienceLevel.BEGINNER) if profile else ExperienceLevel.BEGINNER

        if exp_level == ExperienceLevel.BEGINNER:
            return {
                'assessment_required': False,
                'reason': 'beginner',
                'assessment_type': None,
                'message': 'Diagnostic assessment is optional for beginner learners.',
            }
        return {
            'assessment_required': True,
            'reason': exp_level,
            'assessment_type': 'diagnostic',
            'message': f'Diagnostic assessment is required for {exp_level} level learners.',
        }

    @classmethod
    def list_assessments(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        query: Dict[str, Any] = {'status': 'published'}
        if 'difficulty' in payload and payload['difficulty']:
            query['difficulty'] = payload['difficulty']
        if 'skill_id' in payload and payload['skill_id']:
            query['skill_ids'] = payload['skill_id']
        assessments = AssessmentRepository.find_all_assessments(query)
        return {'assessments': serialize_mongo_list(assessments)}

    @classmethod
    def get_assessment(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        assessment_id = payload.get('assessment_id')
        assessment = AssessmentRepository.find_by_id(assessment_id)
        if not assessment:
            raise NotFoundError('Assessment not found.')

        questions = AssessmentRepository.find_questions_by_assessment(assessment_id)
        serialized = serialize_mongo_doc(assessment)
        sanitized_questions = []
        is_admin = user_context and user_context.get('role') == 'admin'
        for q in questions:
            sq = serialize_mongo_doc(q)
            if not is_admin:
                sq.pop('correct_answer', None)
                sq.pop('explanation', None)
            sanitized_questions.append(sq)

        serialized['questions'] = sanitized_questions
        return serialized

    @classmethod
    def start_attempt(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        assessment_id = payload.get('assessment_id')
        assessment = AssessmentRepository.find_by_id(assessment_id)
        if not assessment:
            raise NotFoundError('Assessment not found.')

        questions = AssessmentRepository.find_questions_by_assessment(assessment_id)
        attempt_doc = {
            'assessment_id': str(assessment_id),
            'user_id': str(user_id),
            'status': AttemptStatus.IN_PROGRESS,
            'answers': {},
            'submitted_at': None,
        }
        attempt_id = AssessmentRepository.create_attempt(attempt_doc)

        sanitized_questions = []
        for q in questions:
            sq = serialize_mongo_doc(q)
            sq.pop('correct_answer', None)
            sq.pop('explanation', None)
            sanitized_questions.append(sq)

        return {
            'attempt_id': attempt_id,
            'assessment_id': assessment_id,
            'title': assessment.get('title'),
            'duration': assessment.get('duration'),
            'questions': sanitized_questions,
        }

    @classmethod
    def submit_attempt(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        data = validate_submit_attempt_payload(payload)
        attempt_id = data['attempt_id']
        submitted_answers = data['answers']

        attempt = AssessmentRepository.find_attempt_by_id(attempt_id)
        if not attempt:
            raise NotFoundError('Assessment attempt not found.')

        if attempt['user_id'] != str(user_id):
            require_owner_or_admin(user_context, attempt['user_id'])

        assessment_id = attempt['assessment_id']
        assessment = AssessmentRepository.find_by_id(assessment_id)
        questions = AssessmentRepository.find_questions_by_assessment(assessment_id)

        passing_score = assessment.get('passing_score', 70.0) if assessment else 70.0
        result_data = DeterministicScoringEngine.calculate_assessment_result(
            questions=questions,
            submitted_answers=submitted_answers,
            passing_score=passing_score
        )

        result_doc = {
            'attempt_id': attempt_id,
            'user_id': str(user_id),
            'assessment_id': assessment_id,
            'score': result_data['score'],
            'total_questions': result_data['total_questions'],
            'percentage': result_data['percentage'],
            'passed': result_data['passed'],
            'skill_scores': result_data['skill_scores'],
            'topic_scores': result_data['topic_scores'],
            'strengths': result_data['strengths'],
            'weaknesses': result_data['weaknesses'],
            'recommendations': [],
            'detailed_breakdown': result_data['detailed_breakdown'],
        }
        result_id = AssessmentRepository.create_result(result_doc)

        AssessmentRepository.update_attempt(attempt_id, {
            'status': AttemptStatus.EVALUATED,
            'submitted_at': now_utc(),
            'answers': submitted_answers,
        })

        for skill_id, stats in result_data['skill_scores'].items():
            verified_score = stats['percentage']
            ProfileRepository.add_verified_skill(str(user_id), {
                'skill_id': skill_id,
                'verified_score': verified_score,
                'verified_at': now_utc(),
            })
            ProgressRepository.upsert_skill_progress(str(user_id), skill_id, {
                'verified_score': verified_score,
                'confidence': 4 if verified_score >= 70.0 else 2,
                'last_assessed': now_utc(),
                'gap': max(0.0, 100.0 - verified_score),
            })

        ProgressRepository.log_activity(str(user_id), {
            'type': 'assessment_completed',
            'assessment_id': assessment_id,
            'attempt_id': attempt_id,
            'score': result_data['score'],
            'percentage': result_data['percentage'],
            'passed': result_data['passed'],
        })

        return serialize_mongo_doc(result_doc)

    @classmethod
    def get_result(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        attempt_id = payload.get('attempt_id')
        result = AssessmentRepository.find_result_by_attempt_id(attempt_id)
        if not result:
            raise NotFoundError('Assessment result not found.')

        require_owner_or_admin(user_context, result['user_id'])
        return serialize_mongo_doc(result)

    @classmethod
    def generate_assessment_ai(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_authenticated(user_context)
        from ai_integrations.assessment_generation import AssessmentGenerationClient
        generated = AssessmentGenerationClient.generate_assessment(payload)

        assessment_doc = {
            'title': generated.get('title', 'AI Generated Diagnostic Assessment'),
            'description': generated.get('description', 'Automatically tailored assessment'),
            'skill_ids': generated.get('skill_ids', []),
            'topic_ids': generated.get('topic_ids', []),
            'difficulty': generated.get('difficulty', 'intermediate'),
            'duration': generated.get('duration', 20),
            'question_count': len(generated.get('questions', [])),
            'passing_score': 70.0,
            'question_distribution': {},
            'status': 'published',
        }
        assessment_id = AssessmentRepository.create_assessment(assessment_doc)

        for q in generated.get('questions', []):
            q_doc = {
                'assessment_id': assessment_id,
                'question': q.get('question'),
                'type': q.get('type', 'single_select'),
                'options': q.get('options', []),
                'correct_answer': q.get('correct_answer'),
                'explanation': q.get('explanation', ''),
                'skill_id': q.get('skill_id', ''),
                'topic': q.get('topic', 'general'),
                'difficulty': q.get('difficulty', 'medium'),
                'learning_objective': q.get('learning_objective', ''),
                'status': 'active',
            }
            AssessmentRepository.create_question(q_doc)

        return cls.get_assessment({'assessment_id': assessment_id}, user_context)

    @classmethod
    def create_assessment_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_assessment_create_payload(payload)
        assessment_id = AssessmentRepository.create_assessment(data)
        created = AssessmentRepository.find_by_id(assessment_id)
        return serialize_mongo_doc(created)

    @classmethod
    def update_assessment_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_assessment_update_payload(payload)
        assessment_id = data['assessment_id']
        AssessmentRepository.update_assessment(assessment_id, data['updates'])
        updated = AssessmentRepository.find_by_id(assessment_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def delete_assessment_admin(cls, assessment_id: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        AssessmentRepository.delete_assessment(assessment_id)
        return {'assessment_id': assessment_id, 'deleted': True}

    @classmethod
    def create_question_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_assessment_question_create_payload(payload)
        q_id = AssessmentRepository.create_question(data)
        created = AssessmentRepository.find_question_by_id(q_id)
        return serialize_mongo_doc(created)

    @classmethod
    def update_question_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        q_id = payload.get('question_id')
        updates = payload.get('updates', payload)
        AssessmentRepository.update_question(q_id, updates)
        updated = AssessmentRepository.find_question_by_id(q_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def delete_question_admin(cls, question_id: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        AssessmentRepository.delete_question(question_id)
        return {'question_id': question_id, 'deleted': True}
