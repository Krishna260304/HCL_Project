from typing import Any, Callable, Dict, Optional
from core.websocket import BaseAsyncConsumer
from users.services import UserService
from profiles.services import ProfileService
from goals.services import GoalService
from onboarding.services import OnboardingService
from learning_history.services import LearningHistoryService
from skills.services import SkillService
from resources.services import ResourceService
from courses.services import CourseService
from projects.services import ProjectService
from assessments.services import AssessmentService
from learning_paths.services import LearningPathService
from recommendations.services import RecommendationService
from progress.services import ProgressService
from feedback.services import FeedbackService
from notifications.services import NotificationService

class UserConsumer(BaseAsyncConsumer):
    require_auth = True
    required_role = None

    handlers = {
        'user.get_self': lambda payload, user: UserService.get_user_self(user),
        'user.update_preferences': lambda payload, user: UserService.update_preferences(payload, user),

        'profile.get': lambda payload, user: ProfileService.get_profile(payload, user),
        'profile.update': lambda payload, user: ProfileService.update_profile(payload, user),

        'goal.create': lambda payload, user: GoalService.create_goal(payload, user),
        'goal.list': lambda payload, user: GoalService.list_goals(payload, user),
        'goal.get': lambda payload, user: GoalService.get_goal(payload, user),
        'goal.update': lambda payload, user: GoalService.update_goal(payload, user),
        'goal.delete': lambda payload, user: GoalService.delete_goal(payload, user),
        'goal.analyze': lambda payload, user: GoalService.analyze_goal_ai(payload, user),

        'onboarding.get': lambda payload, user: OnboardingService.get_session(user),
        'onboarding.save_step': lambda payload, user: OnboardingService.save_step(payload, user),
        'onboarding.complete': lambda payload, user: OnboardingService.complete_onboarding(payload, user),
        'onboarding.questions': lambda payload, user: OnboardingService.get_questions(user),

        'learning_history.create': lambda payload, user: LearningHistoryService.create_entry(payload, user),
        'learning_history.list': lambda payload, user: LearningHistoryService.list_entries(payload, user),
        'learning_history.get': lambda payload, user: LearningHistoryService.get_entry(payload, user),
        'learning_history.update': lambda payload, user: LearningHistoryService.update_entry(payload, user),
        'learning_history.delete': lambda payload, user: LearningHistoryService.delete_entry(payload, user),

        'skill.list': lambda payload, user: SkillService.list_skills(payload, user),
        'skill.get': lambda payload, user: SkillService.get_skill(payload, user),
        'skill.graph': lambda payload, user: SkillService.get_skill_graph(payload, user),
        'skill.prerequisites': lambda payload, user: SkillService.get_prerequisites(payload, user),
        'skill.dependents': lambda payload, user: SkillService.get_dependents(payload, user),

        'resource.search': lambda payload, user: ResourceService.search_resources(payload, user),
        'resource.get': lambda payload, user: ResourceService.get_resource(payload, user),
        'resource.list': lambda payload, user: ResourceService.list_resources(payload, user),

        'course.list': lambda payload, user: CourseService.list_courses(payload, user),
        'course.get': lambda payload, user: CourseService.get_course(payload, user),

        'project.list': lambda payload, user: ProjectService.list_projects(payload, user),
        'project.get': lambda payload, user: ProjectService.get_project(payload, user),

        'assessment.requirements': lambda payload, user: AssessmentService.get_assessment_requirement(payload, user),
        'assessment.list': lambda payload, user: AssessmentService.list_assessments(payload, user),
        'assessment.get': lambda payload, user: AssessmentService.get_assessment(payload, user),
        'assessment.start': lambda payload, user: AssessmentService.start_attempt(payload, user),
        'assessment.submit': lambda payload, user: AssessmentService.submit_attempt(payload, user),
        'assessment.result': lambda payload, user: AssessmentService.get_result(payload, user),
        'assessment.generate_ai': lambda payload, user: AssessmentService.generate_assessment_ai(payload, user),

        'learning_path.get': lambda payload, user: LearningPathService.get_learning_path(payload, user),
        'learning_path.generate': lambda payload, user: LearningPathService.generate_learning_path(payload, user),
        'learning_path.update': lambda payload, user: LearningPathService.update_learning_path(payload, user),
        'learning_path.phase.complete': lambda payload, user: LearningPathService.complete_phase(payload, user),
        'learning_path.phase.skip': lambda payload, user: LearningPathService.skip_phase(payload, user),

        'recommendation.list': lambda payload, user: RecommendationService.list_recommendations(payload, user),
        'recommendation.update_status': lambda payload, user: RecommendationService.update_status(payload, user),

        'progress.get': lambda payload, user: ProgressService.get_progress(payload, user),
        'progress.update': lambda payload, user: ProgressService.update_progress(payload, user),
        'progress.skills': lambda payload, user: ProgressService.get_skill_progress(payload, user),
        'progress.activity': lambda payload, user: ProgressService.get_activity(payload, user),

        'feedback.create': lambda payload, user: FeedbackService.create_feedback(payload, user),
        'feedback.list_self': lambda payload, user: FeedbackService.list_self_feedback(payload, user),

        'notification.list': lambda payload, user: NotificationService.list_notifications(payload, user),
        'notification.mark_read': lambda payload, user: NotificationService.mark_as_read(payload, user),
        'notification.mark_all_read': lambda payload, user: NotificationService.mark_all_as_read(payload, user),
    }
