import pytest
from assessments.services import AssessmentService
from assessments.scoring import DeterministicScoringEngine

def test_deterministic_scoring_engine():
    questions = [
        {
            '_id': 'q1',
            'type': 'single_select',
            'correct_answer': 'Option A',
            'skill_id': 'python',
            'topic': 'syntax',
        },
        {
            '_id': 'q2',
            'type': 'boolean',
            'correct_answer': True,
            'skill_id': 'python',
            'topic': 'types',
        },
        {
            '_id': 'q3',
            'type': 'single_select',
            'correct_answer': 'Django',
            'skill_id': 'web',
            'topic': 'frameworks',
        }
    ]
    submitted_answers = {
        'q1': 'Option A',
        'q2': True,
        'q3': 'Flask',
    }
    result = DeterministicScoringEngine.calculate_assessment_result(questions, submitted_answers, passing_score=60.0)
    assert result['score'] == 2
    assert result['total_questions'] == 3
    assert result['percentage'] == 66.67
    assert result['passed'] is True
    assert 'python' in result['strengths']
    assert 'web' in result['weaknesses']

def test_assessment_attempt_and_submission(admin_account, learner_account):
    admin_context = {
        'user_id': admin_account['user']['id'],
        'email': admin_account['user']['email'],
        'role': 'admin',
    }
    learner_context = {
        'user_id': learner_account['user']['id'],
        'email': learner_account['user']['email'],
        'role': 'learner',
    }
    assessment = AssessmentService.create_assessment_admin({
        'title': 'Python & Backend Diagnostic',
        'difficulty': 'intermediate',
        'passing_score': 50.0,
    }, admin_context)

    q = AssessmentService.create_question_admin({
        'assessment_id': assessment['id'],
        'question': 'What is GIL in CPython?',
        'type': 'single_select',
        'options': ['Global Interpreter Lock', 'General Instruction Level'],
        'correct_answer': 'Global Interpreter Lock',
        'skill_id': 'python',
        'topic': 'concurrency',
    }, admin_context)

    attempt = AssessmentService.start_attempt({'assessment_id': assessment['id']}, learner_context)
    assert 'attempt_id' in attempt
    assert len(attempt['questions']) == 1
    assert 'correct_answer' not in attempt['questions'][0]

    submitted = AssessmentService.submit_attempt({
        'attempt_id': attempt['attempt_id'],
        'answers': {q['id']: 'Global Interpreter Lock'}
    }, learner_context)
    assert submitted['score'] == 1
    assert submitted['percentage'] == 100.0
    assert submitted['passed'] is True
