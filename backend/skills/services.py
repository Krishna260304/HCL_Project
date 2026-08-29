from typing import Any, Dict, List, Optional
from core.permissions import require_authenticated, require_admin
from core.exceptions import NotFoundError, ConflictError
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from skills.repository import SkillRepository
from skills.graph import SkillGraphEngine
from skills.validators import (
    validate_skill_create_payload,
    validate_skill_update_payload,
    validate_relationship_create_payload
)

class SkillService:
    @classmethod
    def list_skills(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        query: Dict[str, Any] = {}
        if 'category' in payload and payload['category']:
            query['category'] = payload['category']
        if 'search' in payload and payload['search']:
            query['name'] = {'$regex': str(payload['search']).strip(), '$options': 'i'}
        skills = SkillRepository.find_all_skills(query)
        return {'skills': serialize_mongo_list(skills)}

    @classmethod
    def get_skill(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        skill_id = payload.get('skill_id')
        skill = SkillRepository.find_by_id(skill_id)
        if not skill:
            raise NotFoundError('Skill not found.')
        return serialize_mongo_doc(skill)

    @classmethod
    def get_skill_graph(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        skills = SkillRepository.find_all_skills()
        relationships = SkillRepository.list_relationships()
        return {
            'nodes': serialize_mongo_list(skills),
            'edges': serialize_mongo_list(relationships),
        }

    @classmethod
    def get_prerequisites(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        skill_id = payload.get('skill_id')
        relationships = SkillRepository.list_relationships()
        prereq_ids = SkillGraphEngine.get_prerequisites_transitive(str(skill_id), relationships)
        prereq_skills = [SkillRepository.find_by_id(pid) for pid in prereq_ids if SkillRepository.find_by_id(pid)]
        return {'skill_id': skill_id, 'prerequisites': serialize_mongo_list(prereq_skills)}

    @classmethod
    def get_dependents(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        skill_id = payload.get('skill_id')
        relationships = SkillRepository.list_relationships()
        dep_ids = SkillGraphEngine.get_dependents_transitive(str(skill_id), relationships)
        dep_skills = [SkillRepository.find_by_id(did) for did in dep_ids if SkillRepository.find_by_id(did)]
        return {'skill_id': skill_id, 'dependents': serialize_mongo_list(dep_skills)}

    @classmethod
    def create_skill_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_skill_create_payload(payload)
        existing = SkillRepository.find_by_name(data['name'])
        if existing:
            raise ConflictError('A skill with this name already exists.')
        skill_id = SkillRepository.create_skill(data)
        created = SkillRepository.find_by_id(skill_id)
        return serialize_mongo_doc(created)

    @classmethod
    def update_skill_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_skill_update_payload(payload)
        skill_id = data['skill_id']
        SkillRepository.update_skill(skill_id, data['updates'])
        updated = SkillRepository.find_by_id(skill_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def delete_skill_admin(cls, skill_id: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        SkillRepository.delete_skill(skill_id)
        return {'skill_id': skill_id, 'deleted': True}

    @classmethod
    def create_relationship_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_relationship_create_payload(payload)
        rel_id = SkillRepository.create_relationship(data)
        return {'relationship_id': rel_id, 'created': True}

    @classmethod
    def delete_relationship_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        source_id = payload.get('source_skill_id')
        target_id = payload.get('target_skill_id')
        rel_type = payload.get('relationship_type', 'prerequisite')
        deleted = SkillRepository.delete_relationship(str(source_id), str(target_id), str(rel_type))
        return {'deleted': deleted}
