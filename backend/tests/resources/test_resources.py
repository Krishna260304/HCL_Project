import pytest
from resources.services import ResourceService

def test_resource_crud_and_search(admin_account):
    admin_context = {
        'user_id': admin_account['user']['id'],
        'email': admin_account['user']['email'],
        'role': 'admin',
    }
    res = ResourceService.create_resource_admin({
        'title': 'Production Django Channels Guide',
        'url': 'https://example.com/channels',
        'type': 'article',
        'difficulty': 'intermediate',
        'skills': ['Django', 'WebSockets'],
    }, admin_context)
    assert res['title'] == 'Production Django Channels Guide'

    search_res = ResourceService.search_resources({'query': 'Channels'}, None)
    assert len(search_res['resources']) >= 1
