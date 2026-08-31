import pytest
from admin_portal.services import AdminService

def test_admin_settings_and_audit(admin_account):
    admin_context = {
        'user_id': admin_account['user']['id'],
        'email': admin_account['user']['email'],
        'role': 'admin',
    }
    updated = AdminService.update_user_status({
        'user_id': admin_account['user']['id'],
        'status': 'active',
        'reason': 'Routine check',
    }, admin_context)
    assert updated['updated'] is True

    audit_logs = AdminService.list_audit_logs({}, admin_context)
    assert len(audit_logs['audit_logs']) >= 1
