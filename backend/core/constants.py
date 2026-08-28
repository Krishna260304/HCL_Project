class Roles:
    LEARNER = 'learner'
    ADMIN = 'admin'
    ALL_ROLES = [LEARNER, ADMIN]

class UserStatus:
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    SUSPENDED = 'suspended'
    RESTRICTED = 'restricted'
    ALL_STATUSES = [ACTIVE, INACTIVE, SUSPENDED, RESTRICTED]

class GoalStatus:
    ACTIVE = 'active'
    COMPLETED = 'completed'
    PAUSED = 'paused'
    CANCELLED = 'cancelled'
    ALL_STATUSES = [ACTIVE, COMPLETED, PAUSED, CANCELLED]

class ResourceType:
    VIDEO = 'video'
    COURSE = 'course'
    ARTICLE = 'article'
    DOCUMENTATION = 'documentation'
    PROJECT = 'project'
    EXERCISE = 'exercise'
    LAB = 'lab'
    QUIZ = 'quiz'
    ALL_TYPES = [VIDEO, COURSE, ARTICLE, DOCUMENTATION, PROJECT, EXERCISE, LAB, QUIZ]

class ResourceStatus:
    DRAFT = 'draft'
    PENDING_REVIEW = 'pending_review'
    APPROVED = 'approved'
    PUBLISHED = 'published'
    UNPUBLISHED = 'unpublished'
    ARCHIVED = 'archived'
    REJECTED = 'rejected'
    ALL_STATUSES = [DRAFT, PENDING_REVIEW, APPROVED, PUBLISHED, UNPUBLISHED, ARCHIVED, REJECTED]

class QuestionType:
    TEXT = 'text'
    SINGLE_SELECT = 'single_select'
    MULTI_SELECT = 'multi_select'
    NUMBER = 'number'
    SLIDER = 'slider'
    DROPDOWN = 'dropdown'
    BOOLEAN = 'boolean'
    ALL_TYPES = [TEXT, SINGLE_SELECT, MULTI_SELECT, NUMBER, SLIDER, DROPDOWN, BOOLEAN]

class RelationshipType:
    PREREQUISITE = 'prerequisite'
    RELATED = 'related'
    ADVANCED = 'advanced'
    ALTERNATIVE = 'alternative'
    PART_OF = 'part_of'
    ALL_TYPES = [PREREQUISITE, RELATED, ADVANCED, ALTERNATIVE, PART_OF]

class LearningHistoryType:
    COURSE = 'course'
    BOOK = 'book'
    TUTORIAL = 'tutorial'
    CERTIFICATION = 'certification'
    UNIVERSITY_SUBJECT = 'university_subject'
    BOOTCAMP = 'bootcamp'
    PROJECT = 'project'
    OTHER = 'other'
    ALL_TYPES = [COURSE, BOOK, TUTORIAL, CERTIFICATION, UNIVERSITY_SUBJECT, BOOTCAMP, PROJECT, OTHER]

class PhaseStatus:
    LOCKED = 'locked'
    UPCOMING = 'upcoming'
    CURRENT = 'current'
    COMPLETED = 'completed'
    SKIPPED = 'skipped'
    ALL_STATUSES = [LOCKED, UPCOMING, CURRENT, COMPLETED, SKIPPED]

class RecommendationStatus:
    RECOMMENDED = 'recommended'
    VIEWED = 'viewed'
    STARTED = 'started'
    COMPLETED = 'completed'
    SAVED = 'saved'
    SKIPPED = 'skipped'
    REJECTED = 'rejected'
    ALL_STATUSES = [RECOMMENDED, VIEWED, STARTED, COMPLETED, SAVED, SKIPPED, REJECTED]

class FeedbackType:
    RESOURCE = 'resource'
    LEARNING_PATH = 'learning_path'
    ASSESSMENT = 'assessment'
    ASSISTANT = 'assistant'
    PROJECT = 'project'
    ALL_TYPES = [RESOURCE, LEARNING_PATH, ASSESSMENT, ASSISTANT, PROJECT]

class NotificationType:
    SYSTEM = 'system'
    LEARNING = 'learning'
    ASSESSMENT = 'assessment'
    RECOMMENDATION = 'recommendation'
    PROGRESS = 'progress'
    SECURITY = 'security'
    ANNOUNCEMENT = 'announcement'
    ALL_TYPES = [SYSTEM, LEARNING, ASSESSMENT, RECOMMENDATION, PROGRESS, SECURITY, ANNOUNCEMENT]

class ChatRole:
    USER = 'user'
    ASSISTANT = 'assistant'
    SYSTEM = 'system'
    ALL_ROLES = [USER, ASSISTANT, SYSTEM]

class ExperienceLevel:
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    EXPERIENCED = 'experienced'
    ALL_LEVELS = [BEGINNER, INTERMEDIATE, ADVANCED, EXPERIENCED]

class AssessmentStatus:
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
    ALL_STATUSES = [DRAFT, PUBLISHED, ARCHIVED]

class AttemptStatus:
    IN_PROGRESS = 'in_progress'
    SUBMITTED = 'submitted'
    EVALUATED = 'evaluated'
    EXPIRED = 'expired'
    ALL_STATUSES = [IN_PROGRESS, SUBMITTED, EVALUATED, EXPIRED]

class ErrorCodes:
    AUTHENTICATION_ERROR = 'AUTHENTICATION_ERROR'
    AUTHORIZATION_ERROR = 'AUTHORIZATION_ERROR'
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    NOT_FOUND = 'NOT_FOUND'
    CONFLICT = 'CONFLICT'
    DATABASE_ERROR = 'DATABASE_ERROR'
    EXTERNAL_SERVICE_ERROR = 'EXTERNAL_SERVICE_ERROR'
    AI_SERVICE_ERROR = 'AI_SERVICE_ERROR'
    RATE_LIMIT_ERROR = 'RATE_LIMIT_ERROR'
    INTERNAL_ERROR = 'INTERNAL_ERROR'

class EventNames:
    PROFILE_UPDATED = 'user.profile.updated'
    GOAL_CREATED = 'goal.created'
    GOAL_UPDATED = 'goal.updated'
    ASSESSMENT_STARTED = 'assessment.started'
    ASSESSMENT_SUBMITTED = 'assessment.submitted'
    ASSESSMENT_COMPLETED = 'assessment.completed'
    SKILL_UPDATED = 'skill.updated'
    LEARNING_PATH_GENERATED = 'learning_path.generated'
    LEARNING_PATH_UPDATED = 'learning_path.updated'
    RESOURCE_RECOMMENDED = 'resource.recommended'
    RESOURCE_COMPLETED = 'resource.completed'
    PROGRESS_UPDATED = 'progress.updated'
    NOTIFICATION_CREATED = 'notification.created'
    CHAT_MESSAGE = 'chat.message'
    ADMIN_USER_UPDATED = 'admin.user.updated'
    ADMIN_RESOURCE_UPDATED = 'admin.resource.updated'
    ADMIN_SETTINGS_UPDATED = 'admin.settings.updated'
    SYSTEM_STATUS_UPDATED = 'system.status.updated'
