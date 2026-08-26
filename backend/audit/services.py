from typing import Any, Dict, Optional
from core.permissions import require_admin
from core.utilities import serialize_mongo_list
from audit.repository import AuditRepository

class AuditService:
    @classmethod
    def log_action(
        cls,
        admin_id: str,
        action: str,
        module: str,
        target_type: str,
        target_id: str,
        before: Optional[Dict[str, Any]] = None,
        after: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> str:
        doc = {
            'admin_id': str(admin_id),
            'action': action,
            'module': module,
            'target_type': target_type,
            'target_id': str(target_id),
            'before': before,
            'after': after,
            'ip_address': ip_address,
            'user_agent': user_agent,
        }
        return AuditRepository.create_log(doc)

    @classmethod
    def list_logs(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        query: Dict[str, Any] = {}
        if 'module' in payload and payload['module']:
            query['module'] = payload['module']
        if 'admin_id' in payload and payload['admin_id']:
            query['admin_id'] = str(payload['admin_id'])
        if 'action' in payload and payload['action']:
            query['action'] = payload['action']
        logs = AuditRepository.find_all(query, skip=0, limit=100)
        return {'audit_logs': serialize_mongo_list(logs)}
