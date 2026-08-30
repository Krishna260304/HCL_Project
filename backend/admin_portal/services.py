from typing import Any, Dict, Optional
from core.permissions import require_admin
from users.services import UserService
from onboarding.services import OnboardingService
from skills.services import SkillService
from resources.services import ResourceService
from courses.services import CourseService
from projects.services import ProjectService
from assessments.services import AssessmentService
from learning_paths.services import LearningPathService
from platform_settings.services import PlatformSettingsService
from audit.services import AuditService
from analytics.services import AnalyticsService
from recommendations.services import RecommendationService

class AdminService:
    @classmethod
    def list_recommendations(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return RecommendationService.list_all_admin(payload, user_context)
    @classmethod
    def list_users(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return UserService.list_users(payload, user_context)

    @classmethod
    def get_user(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return UserService.get_user_by_id(payload.get('user_id'), user_context)

    @classmethod
    def update_user_status(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return UserService.update_status(payload, user_context)

    @classmethod
    def delete_user(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return UserService.delete_user(payload.get('user_id'), user_context)

    @classmethod
    def list_onboarding_questions(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return OnboardingService.list_all_questions_admin(user_context)

    @classmethod
    def create_onboarding_question(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return OnboardingService.create_question_admin(payload, user_context)

    @classmethod
    def update_onboarding_question(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return OnboardingService.update_question_admin(payload, user_context)

    @classmethod
    def delete_onboarding_question(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return OnboardingService.delete_question_admin(payload.get('question_id'), user_context)

    @classmethod
    def create_skill(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return SkillService.create_skill_admin(payload, user_context)

    @classmethod
    def update_skill(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return SkillService.update_skill_admin(payload, user_context)

    @classmethod
    def delete_skill(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return SkillService.delete_skill_admin(payload.get('skill_id'), user_context)

    @classmethod
    def create_skill_relationship(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return SkillService.create_relationship_admin(payload, user_context)

    @classmethod
    def delete_skill_relationship(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return SkillService.delete_relationship_admin(payload, user_context)

    @classmethod
    def create_resource(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return ResourceService.create_resource_admin(payload, user_context)

    @classmethod
    def update_resource(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return ResourceService.update_resource_admin(payload, user_context)

    @classmethod
    def delete_resource(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return ResourceService.delete_resource_admin(payload.get('resource_id'), user_context)

    @classmethod
    def approve_resource(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return ResourceService.approve_resource_admin(payload.get('resource_id'), user_context)

    @classmethod
    def reject_resource(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return ResourceService.reject_resource_admin(payload.get('resource_id'), payload.get('reason', ''), user_context)

    @classmethod
    def create_course(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return CourseService.create_course_admin(payload, user_context)

    @classmethod
    def update_course(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return CourseService.update_course_admin(payload, user_context)

    @classmethod
    def delete_course(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return CourseService.delete_course_admin(payload.get('course_id'), user_context)

    @classmethod
    def create_project(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return ProjectService.create_project_admin(payload, user_context)

    @classmethod
    def update_project(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return ProjectService.update_project_admin(payload, user_context)

    @classmethod
    def delete_project(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return ProjectService.delete_project_admin(payload.get('project_id'), user_context)

    @classmethod
    def create_assessment(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return AssessmentService.create_assessment_admin(payload, user_context)

    @classmethod
    def update_assessment(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return AssessmentService.update_assessment_admin(payload, user_context)

    @classmethod
    def delete_assessment(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return AssessmentService.delete_assessment_admin(payload.get('assessment_id'), user_context)

    @classmethod
    def create_question(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return AssessmentService.create_question_admin(payload, user_context)

    @classmethod
    def update_question(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return AssessmentService.update_question_admin(payload, user_context)

    @classmethod
    def delete_question(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return AssessmentService.delete_question_admin(payload.get('question_id'), user_context)

    @classmethod
    def list_all_learning_paths(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return LearningPathService.list_all_paths_admin(payload, user_context)

    @classmethod
    def override_learning_path(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return LearningPathService.override_path_admin(payload, user_context)

    @classmethod
    def list_audit_logs(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return AuditService.list_logs(payload, user_context)
