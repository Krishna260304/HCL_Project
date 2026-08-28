from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from admin_portal.services import AdminService
from platform_settings.services import PlatformSettingsService
from analytics.services import AnalyticsService

class AdminConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = 'admin'

    handlers = {
        'admin.users.list': lambda payload, user: AdminService.list_users(payload, user),
        'admin.users.get': lambda payload, user: AdminService.get_user(payload, user),
        'admin.users.update_status': lambda payload, user: AdminService.update_user_status(payload, user),
        'admin.users.delete': lambda payload, user: AdminService.delete_user(payload, user),

        'admin.onboarding.questions.list': lambda payload, user: AdminService.list_onboarding_questions(payload, user),
        'admin.onboarding.questions.create': lambda payload, user: AdminService.create_onboarding_question(payload, user),
        'admin.onboarding.questions.update': lambda payload, user: AdminService.update_onboarding_question(payload, user),
        'admin.onboarding.questions.delete': lambda payload, user: AdminService.delete_onboarding_question(payload, user),

        'admin.skills.create': lambda payload, user: AdminService.create_skill(payload, user),
        'admin.skills.update': lambda payload, user: AdminService.update_skill(payload, user),
        'admin.skills.delete': lambda payload, user: AdminService.delete_skill(payload, user),
        'admin.skills.relationships.create': lambda payload, user: AdminService.create_skill_relationship(payload, user),
        'admin.skills.relationships.delete': lambda payload, user: AdminService.delete_skill_relationship(payload, user),

        'admin.resources.create': lambda payload, user: AdminService.create_resource(payload, user),
        'admin.resources.update': lambda payload, user: AdminService.update_resource(payload, user),
        'admin.resources.delete': lambda payload, user: AdminService.delete_resource(payload, user),
        'admin.resources.approve': lambda payload, user: AdminService.approve_resource(payload, user),
        'admin.resources.reject': lambda payload, user: AdminService.reject_resource(payload, user),

        'admin.courses.create': lambda payload, user: AdminService.create_course(payload, user),
        'admin.courses.update': lambda payload, user: AdminService.update_course(payload, user),
        'admin.courses.delete': lambda payload, user: AdminService.delete_course(payload, user),

        'admin.projects.create': lambda payload, user: AdminService.create_project(payload, user),
        'admin.projects.update': lambda payload, user: AdminService.update_project(payload, user),
        'admin.projects.delete': lambda payload, user: AdminService.delete_project(payload, user),

        'admin.assessments.create': lambda payload, user: AdminService.create_assessment(payload, user),
        'admin.assessments.update': lambda payload, user: AdminService.update_assessment(payload, user),
        'admin.assessments.delete': lambda payload, user: AdminService.delete_assessment(payload, user),
        'admin.questions.create': lambda payload, user: AdminService.create_question(payload, user),
        'admin.questions.update': lambda payload, user: AdminService.update_question(payload, user),
        'admin.questions.delete': lambda payload, user: AdminService.delete_question(payload, user),

        'admin.learning_paths.list': lambda payload, user: AdminService.list_all_learning_paths(payload, user),
        'admin.learning_paths.override': lambda payload, user: AdminService.override_learning_path(payload, user),

        'admin.settings.get': lambda payload, user: PlatformSettingsService.get_settings(user),
        'admin.settings.update': lambda payload, user: PlatformSettingsService.update_settings(payload, user),
        'admin.feature_flags.list': lambda payload, user: PlatformSettingsService.list_feature_flags(user),
        'admin.feature_flags.update': lambda payload, user: PlatformSettingsService.update_feature_flag(payload, user),

        'admin.audit.list': lambda payload, user: AdminService.list_audit_logs(payload, user),
        'admin.analytics.overview': lambda payload, user: AnalyticsService.get_overview(payload, user),
    }
