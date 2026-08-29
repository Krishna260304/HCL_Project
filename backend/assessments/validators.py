from typing import Any, Dict
from core.validators import validate_required_fields, validate_object_id, validate_enum
from core.constants import QuestionType, AssessmentStatus

def validate_assessment_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['title'])
    return {
        'title': str(data['title']).strip(),
        'description': str(data.get('description', '')).strip(),
        'skill_ids': data.get('skill_ids', []) if isinstance(data.get('skill_ids'), list) else [],
        'topic_ids': data.get('topic_ids', []) if isinstance(data.get('topic_ids'), list) else [],
        'difficulty': str(data.get('difficulty', 'intermediate')).strip(),
        'duration': max(1, int(data.get('duration', 30))),
        'question_count': max(1, int(data.get('question_count', 10))),
        'passing_score': max(0.0, min(100.0, float(data.get('passing_score', 70.0)))),
        'question_distribution': data.get('question_distribution', {}) if isinstance(data.get('question_distribution'), dict) else {},
        'status': str(data.get('status', AssessmentStatus.PUBLISHED)).strip(),
    }

def validate_assessment_update_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['assessment_id'])
    assessment_id = validate_object_id(data['assessment_id'], 'assessment_id')
    updates: Dict[str, Any] = {}
    for key in ('title', 'description', 'difficulty', 'status'):
        if key in data:
            updates[key] = str(data[key]).strip()
    if 'duration' in data:
        updates['duration'] = max(1, int(data['duration']))
    if 'question_count' in data:
        updates['question_count'] = max(1, int(data['question_count']))
    if 'passing_score' in data:
        updates['passing_score'] = max(0.0, min(100.0, float(data['passing_score'])))
    if 'skill_ids' in data and isinstance(data['skill_ids'], list):
        updates['skill_ids'] = data['skill_ids']
    if 'topic_ids' in data and isinstance(data['topic_ids'], list):
        updates['topic_ids'] = data['topic_ids']
    return {'assessment_id': assessment_id, 'updates': updates}

def validate_assessment_question_create_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['assessment_id', 'question', 'type', 'correct_answer'])
    assessment_id = validate_object_id(data['assessment_id'], 'assessment_id')
    q_type = validate_enum(data['type'], QuestionType.ALL_TYPES, 'type')
    return {
        'assessment_id': assessment_id,
        'question': str(data['question']).strip(),
        'type': q_type,
        'options': data.get('options', []) if isinstance(data.get('options'), list) else [],
        'correct_answer': data['correct_answer'],
        'explanation': str(data.get('explanation', '')).strip(),
        'skill_id': str(data.get('skill_id', '')).strip(),
        'topic': str(data.get('topic', 'general')).strip(),
        'difficulty': str(data.get('difficulty', 'medium')).strip(),
        'learning_objective': str(data.get('learning_objective', '')).strip(),
        'status': str(data.get('status', 'active')).strip(),
    }

def validate_submit_attempt_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    validate_required_fields(data, ['attempt_id', 'answers'])
    attempt_id = validate_object_id(data['attempt_id'], 'attempt_id')
    if not isinstance(data['answers'], dict):
        raise ValueError('Answers must be a key-value mapping of question IDs to submitted answers.')
    return {
        'attempt_id': attempt_id,
        'answers': data['answers'],
    }
