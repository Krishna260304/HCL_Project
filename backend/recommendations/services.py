from typing import Any, Dict, List, Optional
from core.permissions import require_authenticated, require_owner_or_admin
from core.exceptions import NotFoundError
from core.utilities import serialize_mongo_doc, serialize_mongo_list
from recommendations.repository import RecommendationRepository
from recommendations.validators import validate_recommendation_status_payload
from profiles.repository import ProfileRepository
from resources.repository import ResourceRepository

class RecommendationService:
    @classmethod
    def list_recommendations(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        user_id = auth_user['user_id']
        target_user_id = payload.get('user_id', user_id)
        require_owner_or_admin(user_context, target_user_id)

        status = payload.get('status')
        recs = RecommendationRepository.find_by_user_id(target_user_id, status=status)

        if not recs and not status:
            cls.generate_and_store_recommendations(target_user_id)
            recs = RecommendationRepository.find_by_user_id(target_user_id)

        serialized_recs = []
        for r in recs:
            sr = serialize_mongo_doc(r)
            res_id = r.get('resource_id')
            if res_id:
                res = ResourceRepository.find_by_id(res_id)
                if res:
                    sr['resource'] = serialize_mongo_doc(res)
            serialized_recs.append(sr)

        return {'recommendations': serialized_recs}

    @classmethod
    def update_status(cls, payload: Dict[str, Any], user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        auth_user = require_authenticated(user_context)
        data = validate_recommendation_status_payload(payload)
        rec_id = data['recommendation_id']
        status = data['status']

        rec = RecommendationRepository.find_by_id(rec_id)
        if not rec:
            raise NotFoundError('Recommendation not found.')

        require_owner_or_admin(user_context, rec['user_id'])
        RecommendationRepository.update_status(rec_id, status)
        return {'recommendation_id': rec_id, 'status': status, 'updated': True}

    @classmethod
    def generate_and_store_recommendations(cls, user_id: str) -> List[Dict[str, Any]]:
        profile = ProfileRepository.find_by_user_id(user_id) or {}
        available_resources = ResourceRepository.find_all({'status': 'published'}, skip=0, limit=50)

        from ai_integrations.recommendation import RecommendationClient
        input_data = {
            'user_id': str(user_id),
            'experience_level': profile.get('experience_level', 'beginner'),
            'verified_skills': profile.get('verified_skills', []),
            'interests': profile.get('interests', []),
            'learning_preferences': profile.get('learning_preferences', {}),
            'available_hours': profile.get('available_hours', 5),
            'candidate_resources': serialize_mongo_list(available_resources),
        }
        rec_results = RecommendationClient.get_recommendations(input_data)

        created_recs = []
        for item in rec_results.get('recommendations', []):
            rec_doc = {
                'user_id': str(user_id),
                'resource_id': item.get('resource_id'),
                'skill_id': item.get('skill_id'),
                'score': item.get('score', 0.85),
                'reason': item.get('reason', 'Matches your learning goals.'),
                'source': item.get('source', 'ai_recommendation_engine'),
                'status': 'recommended',
            }
            rec_id = RecommendationRepository.create_recommendation(rec_doc)
            created_recs.append(serialize_mongo_doc(RecommendationRepository.find_by_id(rec_id)))

        return created_recs
