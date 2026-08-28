from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from courses.services import CourseService

class CourseConsumer(BaseAsyncConsumer):
    require_auth = False
    required_role = None

    handlers = {
        'course.list': lambda payload, user: CourseService.list_courses(payload, user),
        'course.get': lambda payload, user: CourseService.get_course(payload, user),
    }
