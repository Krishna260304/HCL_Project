"""
Learning Path Generation Service.
"""

from typing import Any, Dict, List, Optional
from app.schemas.learning_path import LearningPathData, LearningPathRequest
from app.utils.ids import generate_request_id
from app.workflows.learning_path.graph import build_learning_path_graph
from app.workflows.learning_path.state import LearningPathWorkflowState


class LearningPathService:
    def __init__(self):
        self.graph = build_learning_path_graph()

    async def generate(self, request: LearningPathRequest) -> LearningPathData:
        req_id = request.request_id or generate_request_id()

        v_skills: Dict[str, float] = {}
        if isinstance(request.verified_skills, dict):
            v_skills = {str(k): float(v) for k, v in request.verified_skills.items()}
        elif isinstance(request.verified_skills, list):
            for item in request.verified_skills:
                if isinstance(item, dict):
                    s_name = item.get("skill_id") or item.get("skill")
                    if s_name:
                        s_score = item.get("verified_score", item.get("score", 0.7))
                        v_skills[str(s_name)] = float(s_score)
                elif isinstance(item, str) and item.strip():
                    v_skills[item.strip()] = 0.7

        gaps: List[Dict[str, Any]] = []
        for g in request.skill_gaps or []:
            if isinstance(g, dict):
                gaps.append(g)
            elif isinstance(g, str):
                gaps.append({"skill": g, "gap_magnitude": 0.5})

        candidates = request.candidate_resources or request.resources or []

        initial_state = LearningPathWorkflowState(
            request_id=req_id,
            user_id=request.user_id,
            goal=request.goal,
            verified_skills=v_skills,
            skill_gaps=gaps,
            skill_graph=request.skill_graph or {},
            candidate_resources=candidates,
            preferences=request.preferences or {},
            constraints=request.constraints or {},
            experience_level=request.experience_level or "intermediate",
            timeline=request.timeline or "8 weeks",
        )

        final_state = await self.graph.ainvoke(initial_state)
        out = final_state.get("final_output") if isinstance(final_state, dict) else getattr(final_state, "final_output", None)
        if isinstance(out, LearningPathData):
            return out
        elif isinstance(out, dict):
            return LearningPathData.model_validate(out)
        raise RuntimeError("Learning path workflow did not return valid output.")


_learning_path_service: Optional[LearningPathService] = None


def get_learning_path_service() -> LearningPathService:
    global _learning_path_service
    if _learning_path_service is None:
        _learning_path_service = LearningPathService()
    return _learning_path_service
