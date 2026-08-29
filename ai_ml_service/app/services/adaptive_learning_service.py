"""
Adaptive Learning Service.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.recommendation import RecommendationItem
from app.schemas.skill import SkillGap
from app.utils.ids import generate_request_id
from app.workflows.adaptive_learning.graph import build_adaptive_learning_graph
from app.workflows.adaptive_learning.state import AdaptiveLearningWorkflowState


class AdaptiveUpdateData(BaseModel):
    updated_skill_scores: Dict[str, float] = Field(default_factory=dict)
    new_skill_gaps: List[SkillGap] = Field(default_factory=list)
    path_changes: List[Dict[str, Any]] = Field(default_factory=list)
    new_recommendations: List[RecommendationItem] = Field(default_factory=list)
    reason: str = ""
    re_rank_resources: bool = False
    adjust_roadmap: bool = False


class AdaptiveLearningService:
    def __init__(self):
        self.graph = build_adaptive_learning_graph()

    async def update(self, payload: Dict[str, Any]) -> AdaptiveUpdateData:
        req_id = payload.get("request_id") or generate_request_id()

        # Parse skill scores
        skill_scores = payload.get("current_skill_scores") or payload.get("skill_scores") or payload.get("verified_skills") or {}
        if isinstance(skill_scores, list):
            s_map = {}
            for s in skill_scores:
                k = s.get("skill_id") or s.get("skill")
                if k:
                    s_map[k] = float(s.get("verified_score", s.get("score", 0.5)))
            skill_scores = s_map

        initial_state = AdaptiveLearningWorkflowState(
            request_id=req_id,
            previous_learning_path=payload.get("previous_learning_path") or payload.get("current_learning_path") or {},
            latest_assessment=payload.get("latest_assessment") or payload.get("assessment_results") or {},
            current_skill_scores=skill_scores,
            progress=payload.get("progress") or {},
            goal=payload.get("goal"),
        )

        final_state = await self.graph.ainvoke(initial_state)

        updated_scores = final_state.get("updated_skill_scores") if isinstance(final_state, dict) else getattr(final_state, "updated_skill_scores", {})
        new_gaps = final_state.get("new_skill_gaps") if isinstance(final_state, dict) else getattr(final_state, "new_skill_gaps", [])
        path_changes = final_state.get("path_changes") if isinstance(final_state, dict) else getattr(final_state, "path_changes", [])
        new_recs = final_state.get("new_recommendations") if isinstance(final_state, dict) else getattr(final_state, "new_recommendations", [])
        reason = final_state.get("reason") if isinstance(final_state, dict) else getattr(final_state, "reason", "")
        re_rank = final_state.get("re_rank_resources") if isinstance(final_state, dict) else getattr(final_state, "re_rank_resources", False)
        adj_roadmap = final_state.get("adjust_roadmap") if isinstance(final_state, dict) else getattr(final_state, "adjust_roadmap", False)

        return AdaptiveUpdateData(
            updated_skill_scores=updated_scores,
            new_skill_gaps=new_gaps,
            path_changes=path_changes,
            new_recommendations=new_recs,
            reason=reason,
            re_rank_resources=re_rank,
            adjust_roadmap=adj_roadmap,
        )


_adaptive_service: Optional[AdaptiveLearningService] = None


def get_adaptive_learning_service() -> AdaptiveLearningService:
    global _adaptive_service
    if _adaptive_service is None:
        _adaptive_service = AdaptiveLearningService()
    return _adaptive_service
