import pytest
from projects.services import ProjectService

def test_project_crud(admin_account):
    admin_context = {
        'user_id': admin_account['user']['id'],
        'email': admin_account['user']['email'],
        'role': 'admin',
    }
    proj = ProjectService.create_project_admin({
        'title': 'Build a Real-Time Chat Engine',
        'difficulty': 'intermediate',
        'skills': ['Python', 'Channels'],
    }, admin_context)
    assert proj['title'] == 'Build a Real-Time Chat Engine'

    list_res = ProjectService.list_projects({}, None)
    assert len(list_res['projects']) >= 1
