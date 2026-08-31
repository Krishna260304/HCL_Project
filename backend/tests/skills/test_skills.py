import pytest
from skills.services import SkillService

def test_skill_and_graph_operations(admin_account):
    admin_context = {
        'user_id': admin_account['user']['id'],
        'email': admin_account['user']['email'],
        'role': 'admin',
    }
    s1 = SkillService.create_skill_admin({
        'name': 'Python Basics',
        'category': 'Programming',
    }, admin_context)
    s2 = SkillService.create_skill_admin({
        'name': 'Django Framework',
        'category': 'Web Development',
    }, admin_context)

    SkillService.create_relationship_admin({
        'source_skill_id': s1['id'],
        'target_skill_id': s2['id'],
        'relationship_type': 'prerequisite',
    }, admin_context)

    graph = SkillService.get_skill_graph({}, None)
    assert len(graph['nodes']) == 2
    assert len(graph['edges']) == 1

    prereqs = SkillService.get_prerequisites({'skill_id': s2['id']}, None)
    assert len(prereqs['prerequisites']) == 1
    assert prereqs['prerequisites'][0]['id'] == s1['id']
