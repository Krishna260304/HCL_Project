from typing import Any, Dict, Optional
from core.permissions import require_admin
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from platform_settings.repository import SettingsRepository
from platform_settings.validators import validate_platform_settings_update_payload, validate_feature_flag_update_payload
from audit.services import AuditService

class PlatformSettingsService:
    @classmethod
    def get_settings(cls, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        settings = SettingsRepository.get_settings()
        return serialize_mongo_doc(settings)

    @classmethod
    def update_settings(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        before = SettingsRepository.get_settings()
        updates = validate_platform_settings_update_payload(payload.get('settings', payload))
        updated = SettingsRepository.update_settings(updates)

        AuditService.log_action(
            admin_id=user_context['user_id'],
            action='settings.updated',
            module='platform_settings',
            target_type='platform_settings',
            target_id='global_config',
            before=serialize_mongo_doc(before),
            after=serialize_mongo_doc(updated)
        )
        return serialize_mongo_doc(updated)

    @classmethod
    def list_feature_flags(cls, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        flags = SettingsRepository.list_flags()
        return {'flags': serialize_mongo_list(flags)}

    @classmethod
    def update_feature_flag(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        require_admin(user_context)
        data = validate_feature_flag_update_payload(payload)
        SettingsRepository.update_flag(data['name'], data['enabled'], user_context['user_id'])

        AuditService.log_action(
            admin_id=user_context['user_id'],
            action='feature_flag.updated',
            module='platform_settings',
            target_type='feature_flag',
            target_id=data['name'],
            after={'enabled': data['enabled']}
        )
        return {'name': data['name'], 'enabled': data['enabled'], 'updated': True}
