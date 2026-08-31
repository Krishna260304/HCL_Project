import json
import uuid
import urllib.parse
from typing import Any, Callable, Dict, Optional
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from core.responses import success_response, error_response, event_message
from core.exceptions import BaseAppException, AuthenticationError, AuthorizationError
from core.constants import ErrorCodes, Roles
from authentication.tokens import decode_token

class BaseAsyncConsumer(AsyncJsonWebsocketConsumer):
    handlers: Dict[str, Callable] = {}
    require_auth: bool = True
    required_role: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user: Optional[Dict[str, Any]] = None
        self.connection_id: str = str(uuid.uuid4())
        self.user_group: Optional[str] = None
        self.role_group: Optional[str] = None

    async def connect(self) -> None:
        await self.accept()
        query_string = self.scope.get('query_string', b'').decode('utf-8')
        params = urllib.parse.parse_qs(query_string)
        token_list = params.get('token', [])
        token = token_list[0] if token_list else None

        if token:
            await self._authenticate_token(token)

        if self.require_auth and not self.user:
            return

        if self.required_role and self.user and self.user.get('role') != self.required_role:
            await self.send_json(error_response(
                action='connect',
                code=ErrorCodes.AUTHORIZATION_ERROR,
                message=f'Role {self.required_role} required.'
            ))
            await self.close(code=4403)
            return

        await self._register_channels()

    async def disconnect(self, close_code: int) -> None:
        await self._unregister_channels()

    async def _authenticate_token(self, token: str) -> bool:
        try:
            payload = await sync_to_async(decode_token)(token)
            if payload and payload.get('type') == 'access':
                self.user = {
                    'user_id': payload.get('user_id'),
                    'email': payload.get('email'),
                    'role': payload.get('role'),
                }
                return True
        except Exception:
            self.user = None
        return False

    async def _register_channels(self) -> None:
        if self.user and self.channel_name:
            self.user_group = f"user_{self.user.get('user_id')}"
            self.role_group = f"role_{self.user.get('role')}"
            await self.channel_layer.group_add(self.user_group, self.channel_name)
            await self.channel_layer.group_add(self.role_group, self.channel_name)
            await self.channel_layer.group_add('broadcast_all', self.channel_name)

    async def _unregister_channels(self) -> None:
        if self.user_group and self.channel_name:
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        if self.role_group and self.channel_name:
            await self.channel_layer.group_discard(self.role_group, self.channel_name)
        if self.channel_name:
            await self.channel_layer.group_discard('broadcast_all', self.channel_name)

    async def receive_json(self, content: Any, **kwargs) -> None:
        if not isinstance(content, dict):
            await self.send_json(error_response(
                action='unknown',
                code=ErrorCodes.VALIDATION_ERROR,
                message='Message content must be a JSON object.'
            ))
            return

        action = content.get('action', '')
        request_id = content.get('request_id')
        payload = content.get('payload') if content.get('payload') is not None else content.get('data', {})
        if not isinstance(payload, dict):
            payload = {}

        if action == 'ping':
            await self.send_json(success_response(action='pong', request_id=request_id, data={'timestamp': content.get('timestamp')}))
            return

        if action == 'auth.authenticate':
            token = payload.get('token')
            if token and await self._authenticate_token(token):
                await self._register_channels()
                await self.send_json(success_response(
                    action=action,
                    request_id=request_id,
                    data={'authenticated': True, 'user': self.user}
                ))
            else:
                await self.send_json(error_response(
                    action=action,
                    request_id=request_id,
                    code=ErrorCodes.AUTHENTICATION_ERROR,
                    message='Invalid or expired token.'
                ))
            return

        if self.require_auth and not self.user:
            await self.send_json(error_response(
                action=action,
                request_id=request_id,
                code=ErrorCodes.AUTHENTICATION_ERROR,
                message='Authentication required for this operation. Send token via auth.authenticate action or query parameter.'
            ))
            return

        if self.required_role and self.user.get('role') != self.required_role:
            await self.send_json(error_response(
                action=action,
                request_id=request_id,
                code=ErrorCodes.AUTHORIZATION_ERROR,
                message=f'Role {self.required_role} required for this endpoint.'
            ))
            return

        handler = self.get_handler(action)
        if not handler:
            await self.send_json(error_response(
                action=action,
                request_id=request_id,
                code=ErrorCodes.NOT_FOUND,
                message=f'Action "{action}" is not supported by this consumer.'
            ))
            return

        try:
            response_data = await self.dispatch_handler(handler, payload, request_id)
            if action in ('auth.login', 'auth.register') and isinstance(response_data, dict):
                tokens = response_data.get('tokens', {})
                access_token = tokens.get('access_token')
                if access_token:
                    await self._authenticate_token(access_token)
                    await self._register_channels()
            await self.send_json(success_response(
                action=action,
                request_id=request_id,
                data=response_data
            ))
        except BaseAppException as exc:
            await self.send_json(error_response(
                action=action,
                request_id=request_id,
                code=exc.code,
                message=exc.message,
                details=exc.details
            ))
        except Exception as exc:
            await self.send_json(error_response(
                action=action,
                request_id=request_id,
                code=ErrorCodes.INTERNAL_ERROR,
                message='An unexpected internal error occurred.',
                details={'error': str(exc)}
            ))

    def get_handler(self, action: str) -> Optional[Callable]:
        return self.handlers.get(action)

    async def dispatch_handler(self, handler: Callable, payload: Dict[str, Any], request_id: Optional[str]) -> Any:
        return await sync_to_async(handler)(payload, self.user)

    async def broadcast_event(self, event_type: str, data: Any) -> None:
        await self.send_json(event_message(event=event_type, data=data))

    async def channel_event(self, event: Dict[str, Any]) -> None:
        await self.send_json(event_message(event=event.get('event', 'unknown'), data=event.get('data')))

async def broadcast_to_user(user_id: str, event_name: str, data: Any) -> None:
    channel_layer = get_channel_layer()
    if channel_layer:
        await channel_layer.group_send(
            f"user_{user_id}",
            {
                'type': 'channel_event',
                'event': event_name,
                'data': data
            }
        )

async def broadcast_to_role(role: str, event_name: str, data: Any) -> None:
    channel_layer = get_channel_layer()
    if channel_layer:
        await channel_layer.group_send(
            f"role_{role}",
            {
                'type': 'channel_event',
                'event': event_name,
                'data': data
            }
        )

async def broadcast_to_all(event_name: str, data: Any) -> None:
    channel_layer = get_channel_layer()
    if channel_layer:
        await channel_layer.group_send(
            'broadcast_all',
            {
                'type': 'channel_event',
                'event': event_name,
                'data': data
            }
        )

class UnifiedGatewayConsumer(BaseAsyncConsumer):
    require_auth = False
    required_role = None

    def get_handler(self, action: str) -> Optional[Callable]:
        from authentication.services import AuthService
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
        from chat.services import ChatService
        from admin_portal.services import AdminService
        from platform_settings.services import PlatformSettingsService
        from analytics.services import AnalyticsService

        gateway_registry = {
            'auth.register': lambda payload, user: AuthService.register_learner(payload),
            'auth.login': lambda payload, user: AuthService.login(payload),
            'auth.refresh': lambda payload, user: AuthService.refresh_token(payload),
            'auth.password_reset_request': lambda payload, user: AuthService.request_password_reset(payload),
            'auth.password_reset_confirm': lambda payload, user: AuthService.confirm_password_reset(payload),
            'auth.change_password': lambda payload, user: AuthService.change_password(payload, user),
            'auth.logout': lambda payload, user: AuthService.logout(payload, user),

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

            'chat.send': lambda payload, user: ChatService.send_message(payload, user),
            'chat.conversations': lambda payload, user: ChatService.list_conversations(payload, user),
            'chat.history': lambda payload, user: ChatService.get_conversation_history(payload, user),
            'chat.create_conversation': lambda payload, user: ChatService.create_conversation(payload, user),

            'admin.users.list': lambda payload, user: AdminService.list_users(payload, user),
            'admin.users.get': lambda payload, user: AdminService.get_user(payload, user),
            'admin.users.update_status': lambda payload, user: AdminService.update_user_status(payload, user),
            'admin.users.delete': lambda payload, user: AdminService.delete_user(payload, user),
            'admin.recommendations.list': lambda payload, user: AdminService.list_recommendations(payload, user),

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
        return gateway_registry.get(action)
