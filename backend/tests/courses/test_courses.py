import pytest
from courses.services import CourseService

def test_course_crud(admin_account):
    admin_context = {
        'user_id': admin_account['user']['id'],
        'email': admin_account['user']['email'],
        'role': 'admin',
    }
    course = CourseService.create_course_admin({
        'title': 'Advanced Python Mastery',
        'provider': 'LearnPath AI',
        'difficulty': 'advanced',
    }, admin_context)
    assert course['title'] == 'Advanced Python Mastery'

    mod = CourseService.create_module_admin({
        'course_id': course['id'],
        'title': 'Module 1: Concurrency & AsyncIO',
        'order': 1,
    }, admin_context)
    assert mod['created'] is True

    fetched = CourseService.get_course({'course_id': course['id']}, None)
    assert len(fetched['modules_detail']) == 1
