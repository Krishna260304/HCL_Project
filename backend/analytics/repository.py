from typing import Any, Dict, List
from database.mongo import get_database
from database.collections import Collections

class AnalyticsRepository:
    @staticmethod
    def get_db():
        return get_database()

    @classmethod
    def get_overview_metrics(cls) -> Dict[str, Any]:
        db = cls.get_db()
        total_users = db[Collections.USERS].count_documents({})
        active_users = db[Collections.USERS].count_documents({'status': 'active'})
        learners_count = db[Collections.USERS].count_documents({'role': 'learner'})

        total_goals = db[Collections.GOALS].count_documents({})
        active_goals = db[Collections.GOALS].count_documents({'status': 'active'})
        completed_goals = db[Collections.GOALS].count_documents({'status': 'completed'})

        total_skills = db[Collections.SKILLS].count_documents({})
        total_resources = db[Collections.RESOURCES].count_documents({})
        total_courses = db[Collections.COURSES].count_documents({})
        total_projects = db[Collections.PROJECTS].count_documents({})

        total_assessments = db[Collections.ASSESSMENTS].count_documents({})
        total_attempts = db[Collections.ASSESSMENT_ATTEMPTS].count_documents({})
        total_results = db[Collections.ASSESSMENT_RESULTS].count_documents({})

        avg_score_pipeline = [
            {'$group': {'_id': None, 'avg_percentage': {'$avg': '$percentage'}, 'passed_count': {'$sum': {'$cond': ['$passed', 1, 0]}}}}
        ]
        score_stats = list(db[Collections.ASSESSMENT_RESULTS].aggregate(avg_score_pipeline))
        avg_score = round(score_stats[0]['avg_percentage'], 2) if score_stats and score_stats[0].get('avg_percentage') else 0.0
        passed_attempts = score_stats[0]['passed_count'] if score_stats else 0

        total_learning_paths = db[Collections.LEARNING_PATHS].count_documents({})
        completed_paths = db[Collections.LEARNING_PATHS].count_documents({'status': 'completed'})

        return {
            'users': {
                'total': total_users,
                'active': active_users,
                'learners': learners_count,
            },
            'goals': {
                'total': total_goals,
                'active': active_goals,
                'completed': completed_goals,
            },
            'catalog': {
                'skills': total_skills,
                'resources': total_resources,
                'courses': total_courses,
                'projects': total_projects,
            },
            'assessments': {
                'total': total_assessments,
                'attempts': total_attempts,
                'completed': total_results,
                'average_score': avg_score,
                'passed_count': passed_attempts,
            },
            'learning_paths': {
                'total': total_learning_paths,
                'completed': completed_paths,
            },
        }
