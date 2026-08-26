from typing import Any, Dict, Optional
from core.permissions import require_authenticated, require_admin
from core.exceptions import NotFoundError
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from courses.repository import CourseRepository
from courses.validators import (
    validate_course_create_payload,
    validate_course_update_payload,
    validate_module_create_payload
)

class CourseService:
    @classmethod
    def list_courses(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        query: Dict[str, Any] = {'status': 'published'}
        if 'difficulty' in payload and payload['difficulty']:
            query['difficulty'] = payload['difficulty']
        courses = CourseRepository.find_all(query)
        return {'courses': serialize_mongo_list(courses)}

    @classmethod
    def get_course(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        course_id = payload.get('course_id')
        course = CourseRepository.find_by_id(course_id)
        if not course:
            raise NotFoundError('Course not found.')
        modules = CourseRepository.find_modules_by_course(course_id)
        serialized = serialize_mongo_doc(course)
        serialized['modules_detail'] = serialize_mongo_list(modules)
        return serialized

    @classmethod
    def create_course_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_course_create_payload(payload)
        course_id = CourseRepository.create_course(data)
        created = CourseRepository.find_by_id(course_id)
        return serialize_mongo_doc(created)

    @classmethod
    def update_course_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_course_update_payload(payload)
        course_id = data['course_id']
        CourseRepository.update_course(course_id, data['updates'])
        updated = CourseRepository.find_by_id(course_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def delete_course_admin(cls, course_id: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        CourseRepository.delete_course(course_id)
        return {'course_id': course_id, 'deleted': True}

    @classmethod
    def create_module_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_module_create_payload(payload)
        module_id = CourseRepository.create_module(data)
        return {'module_id': module_id, 'created': True}
