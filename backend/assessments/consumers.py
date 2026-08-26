from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from assessments.services import AssessmentService

class AssessmentConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'assessment.requirements': lambda payload, user: AssessmentService.get_assessment_requirement(payload, user),
        'assessment.list': lambda payload, user: AssessmentService.list_assessments(payload, user),
        'assessment.get': lambda payload, user: AssessmentService.get_assessment(payload, user),
        'assessment.start': lambda payload, user: AssessmentService.start_attempt(payload, user),
        'assessment.submit': lambda payload, user: AssessmentService.submit_attempt(payload, user),
        'assessment.result': lambda payload, user: AssessmentService.get_result(payload, user),
        'assessment.generate_ai': lambda payload, user: AssessmentService.generate_assessment_ai(payload, user),
    }
