"""
Recommendation Service.
"""

from typing import Any, Dict, List, Optional
from app.schemas.recommendation import RecommendationData, RecommendationRequest
from app.utils.ids import generate_request_id
from app.workflows.recommendation.graph import build_recommendation_graph
from app.workflows.recommendation.state import RecommendationWorkflowState


class RecommendationService:
    def __init__(self):
        self.graph = build_recommendation_graph()

    async def generate(self, request: RecommendationRequest) -> RecommendationData:
        req_id = request.request_id or generate_request_id()

        # Normalize verified_skills to Dict[str, float]
        v_skills: Dict[str, float] = {}
        if isinstance(request.verified_skills, dict):
            v_skills = {str(k): float(v) for k, v in request.verified_skills.items()}
        elif isinstance(request.verified_skills, list):
            for item in request.verified_skills:
                s_name = item.get("skill_id") or item.get("skill")
                if s_name:
                    s_score = item.get("verified_score", item.get("score", 0.7))
                    v_skills[s_name] = float(s_score)

        # Normalize candidates from candidates or resources
        candidates = request.candidate_resources or request.resources or []

        # Normalize skill_gaps
        gaps: List[Dict[str, Any]] = []
        for g in request.skill_gaps or []:
            if isinstance(g, dict):
                gaps.append(g)
            elif isinstance(g, str):
                gaps.append({"skill": g, "gap_magnitude": 0.5})

        initial_state = RecommendationWorkflowState(
            request_id=req_id,
            user_id=request.user_id,
            learner_profile=request.learner_profile or {},
            verified_skills=v_skills,
            skill_gaps=gaps,
            goal=request.goal,
            candidate_resources=candidates,
            preferences=request.preferences or {},
            constraints=request.constraints or {},
            learning_history=request.learning_history or [],
            limit=request.limit or 10,
        )

        final_state = await self.graph.ainvoke(initial_state)
        out = final_state.get("final_output") if isinstance(final_state, dict) else getattr(final_state, "final_output", None)
        if isinstance(out, RecommendationData):
            return out
        elif isinstance(out, dict):
            return RecommendationData.model_validate(out)
        raise RuntimeError("Recommendation workflow did not return valid output.")


_recommendation_service: Optional[RecommendationService] = None


def get_recommendation_service() -> RecommendationService:
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService()
    return _recommendation_service
