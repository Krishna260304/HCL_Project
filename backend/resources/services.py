from typing import Any, Dict, Optional
from core.permissions import require_authenticated, require_admin
from core.constants import ResourceStatus
from core.exceptions import NotFoundError
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from resources.repository import ResourceRepository
from resources.validators import (
    validate_resource_create_payload,
    validate_resource_update_payload,
    validate_resource_search_payload
)

class ResourceService:
    @classmethod
    def search_resources(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        params = validate_resource_search_payload(payload)
        pagination = params['pagination']
        resources = ResourceRepository.search(
            text_query=params['text_query'],
            skills=params['skills'],
            difficulty=params['difficulty'],
            res_type=params['type'],
            status=ResourceStatus.PUBLISHED,
            skip=pagination['skip'],
            limit=pagination['page_size']
        )
        return {
            'page': pagination['page'],
            'page_size': pagination['page_size'],
            'resources': serialize_mongo_list(resources),
        }

    @classmethod
    def get_resource(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        resource_id = payload.get('resource_id')
        res = ResourceRepository.find_by_id(resource_id)
        if not res:
            raise NotFoundError('Resource not found.')
        return serialize_mongo_doc(res)

    @classmethod
    def list_resources(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        query: Dict[str, Any] = {'status': ResourceStatus.PUBLISHED}
        if 'type' in payload and payload['type']:
            query['type'] = payload['type']
        if 'difficulty' in payload and payload['difficulty']:
            query['difficulty'] = payload['difficulty']
        resources = ResourceRepository.find_all(query, skip=0, limit=50)
        return {'resources': serialize_mongo_list(resources)}

    @classmethod
    def create_resource_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_resource_create_payload(payload)
        res_id = ResourceRepository.create_resource(data)
        created = ResourceRepository.find_by_id(res_id)
        return serialize_mongo_doc(created)

    @classmethod
    def update_resource_admin(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_resource_update_payload(payload)
        res_id = data['resource_id']
        ResourceRepository.update_resource(res_id, data['updates'])
        updated = ResourceRepository.find_by_id(res_id)
        return serialize_mongo_doc(updated)

    @classmethod
    def delete_resource_admin(cls, resource_id: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        ResourceRepository.delete_resource(resource_id)
        return {'resource_id': resource_id, 'deleted': True}

    @classmethod
    def approve_resource_admin(cls, resource_id: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        ResourceRepository.update_resource(resource_id, {'status': ResourceStatus.PUBLISHED})
        return {'resource_id': resource_id, 'status': ResourceStatus.PUBLISHED}

    @classmethod
    def reject_resource_admin(cls, resource_id: str, reason: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        ResourceRepository.update_resource(resource_id, {'status': ResourceStatus.REJECTED, 'rejection_reason': reason})
        return {'resource_id': resource_id, 'status': ResourceStatus.REJECTED}
