from pymongo import ASCENDING, DESCENDING
from database.mongo import get_database
from database.collections import Collections

def create_indexes() -> None:
    db = get_database()

    db[Collections.USERS].create_index([('email', ASCENDING)], unique=True)
    db[Collections.USERS].create_index([('role', ASCENDING)])
    db[Collections.USERS].create_index([('status', ASCENDING)])
    db[Collections.USERS].create_index([('created_at', DESCENDING)])

    db[Collections.PROFILES].create_index([('user_id', ASCENDING)], unique=True)

    db[Collections.GOALS].create_index([('user_id', ASCENDING)])
    db[Collections.GOALS].create_index([('status', ASCENDING)])
    db[Collections.GOALS].create_index([('created_at', DESCENDING)])

    db[Collections.ONBOARDING_SESSIONS].create_index([('user_id', ASCENDING)], unique=True)
    db[Collections.ONBOARDING_QUESTIONS].create_index([('order', ASCENDING)])
    db[Collections.ONBOARDING_QUESTIONS].create_index([('enabled', ASCENDING)])

    db[Collections.SKILLS].create_index([('name', ASCENDING)], unique=True)
    db[Collections.SKILLS].create_index([('category', ASCENDING)])
    db[Collections.SKILLS].create_index([('status', ASCENDING)])

    db[Collections.SKILL_RELATIONSHIPS].create_index([('source_skill_id', ASCENDING), ('target_skill_id', ASCENDING), ('relationship_type', ASCENDING)], unique=True)
    db[Collections.SKILL_RELATIONSHIPS].create_index([('source_skill_id', ASCENDING)])
    db[Collections.SKILL_RELATIONSHIPS].create_index([('target_skill_id', ASCENDING)])

    db[Collections.LEARNING_HISTORY].create_index([('user_id', ASCENDING)])
    db[Collections.LEARNING_HISTORY].create_index([('type', ASCENDING)])

    db[Collections.RESOURCES].create_index([('source', ASCENDING)])
    db[Collections.RESOURCES].create_index([('status', ASCENDING)])
    db[Collections.RESOURCES].create_index([('skills', ASCENDING)])
    db[Collections.RESOURCES].create_index([('created_at', DESCENDING)])

    db[Collections.COURSES].create_index([('status', ASCENDING)])
    db[Collections.COURSES].create_index([('provider', ASCENDING)])
    db[Collections.COURSE_MODULES].create_index([('course_id', ASCENDING), ('order', ASCENDING)])

    db[Collections.PROJECTS].create_index([('status', ASCENDING)])
    db[Collections.PROJECTS].create_index([('difficulty', ASCENDING)])

    db[Collections.ASSESSMENTS].create_index([('skill_ids', ASCENDING)])
    db[Collections.ASSESSMENTS].create_index([('status', ASCENDING)])
    db[Collections.QUESTIONS].create_index([('skill_id', ASCENDING)])
    db[Collections.QUESTIONS].create_index([('status', ASCENDING)])

    db[Collections.ASSESSMENT_ATTEMPTS].create_index([('user_id', ASCENDING)])
    db[Collections.ASSESSMENT_ATTEMPTS].create_index([('assessment_id', ASCENDING)])
    db[Collections.ASSESSMENT_ATTEMPTS].create_index([('status', ASCENDING)])

    db[Collections.ASSESSMENT_RESULTS].create_index([('attempt_id', ASCENDING)], unique=True)
    db[Collections.ASSESSMENT_RESULTS].create_index([('user_id', ASCENDING)])
    db[Collections.ASSESSMENT_RESULTS].create_index([('assessment_id', ASCENDING)])

    db[Collections.LEARNING_PATHS].create_index([('user_id', ASCENDING)])
    db[Collections.LEARNING_PATHS].create_index([('status', ASCENDING)])

    db[Collections.RECOMMENDATIONS].create_index([('user_id', ASCENDING)])
    db[Collections.RECOMMENDATIONS].create_index([('status', ASCENDING)])
    db[Collections.RECOMMENDATIONS].create_index([('score', DESCENDING)])

    db[Collections.PROGRESS].create_index([('user_id', ASCENDING), ('learning_path_id', ASCENDING)])
    db[Collections.SKILL_PROGRESS].create_index([('user_id', ASCENDING), ('skill_id', ASCENDING)], unique=True)
    db[Collections.LEARNING_ACTIVITY].create_index([('user_id', ASCENDING), ('timestamp', DESCENDING)])

    db[Collections.FEEDBACK].create_index([('user_id', ASCENDING)])
    db[Collections.FEEDBACK].create_index([('resource_id', ASCENDING)])
    db[Collections.FEEDBACK].create_index([('assessment_id', ASCENDING)])

    db[Collections.NOTIFICATIONS].create_index([('user_id', ASCENDING)])
    db[Collections.NOTIFICATIONS].create_index([('read', ASCENDING)])
    db[Collections.NOTIFICATIONS].create_index([('created_at', DESCENDING)])

    db[Collections.CONVERSATIONS].create_index([('user_id', ASCENDING)])
    db[Collections.CONVERSATIONS].create_index([('updated_at', DESCENDING)])
    db[Collections.MESSAGES].create_index([('conversation_id', ASCENDING), ('created_at', ASCENDING)])

    db[Collections.AUDIT_LOGS].create_index([('admin_id', ASCENDING)])
    db[Collections.AUDIT_LOGS].create_index([('timestamp', DESCENDING)])
    db[Collections.AUDIT_LOGS].create_index([('action', ASCENDING)])

    db[Collections.MODERATION_ITEMS].create_index([('status', ASCENDING)])
    db[Collections.FEATURE_FLAGS].create_index([('name', ASCENDING)], unique=True)
    db[Collections.PLATFORM_SETTINGS].create_index([('key', ASCENDING)], unique=True)
