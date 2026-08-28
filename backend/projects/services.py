from typing import Any, Dict, Optional
from core.permissions import require_authenticated, require_admin
from core.exceptions import NotFoundError
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from projects.repository import ProjectRepository
from projects.validators import (
    validate_project_create_payload,
    validate_project_update_payload
)

class ProjectService:
    @classmethod
    def list_projects(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        query: Dict[str, Any] = {'status': 'published'}
        if 'difficulty' in payload and payload['difficulty']:
            query['difficulty'] = payload['difficulty']
        projects = ProjectRepository.find_all(query)
        return {'projects': serialize_mongo_list(projects)}

    @classmethod
    def get_project(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        project_id = payload.get('project_id')
        project = ProjectRepository.find_by_id(project_id)
        if not project:
            raise NotFoundError('Project not found.')
        return serialize_mongo_doc(project)

    @classmethod
    def create_project_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_project_create_payload(payload)
        project_id = ProjectRepository.create_project(data)
        created = ProjectRepository.find_by_id(project_id)
        return serialize_mongo_doc(created)

    @classmethod
    def update_project_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_project_update_payload(payload)
        project_id = data['project_id']
        ProjectRepository.update_project(project_id, data['updates'])
        updated = ProjectRepository.find_by_id(project_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def delete_project_admin(cls, project_id: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        ProjectRepository.delete_project(project_id)
        return {'project_id': project_id, 'deleted': True}
