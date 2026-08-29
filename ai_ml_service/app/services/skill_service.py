"""
Skill Analysis Service.
"""

from typing import Optional
from app.schemas.skill import SkillAnalysisData, SkillAnalysisRequest
from app.utils.ids import generate_request_id
from app.workflows.skill_analysis.graph import build_skill_analysis_graph
from app.workflows.skill_analysis.state import SkillAnalysisWorkflowState


class SkillService:
    def __init__(self):
        self.graph = build_skill_analysis_graph()

    async def analyze(self, request: SkillAnalysisRequest) -> SkillAnalysisData:
        req_id = request.request_id or generate_request_id()
        initial_state = SkillAnalysisWorkflowState(
            request_id=req_id,
            learner_profile=request.learner_profile or {},
            assessment_results=request.assessment_results or [],
            verified_skills_input=request.verified_skills or [],
            self_reported_skills=request.self_reported_skills or {},
            learning_history=request.learning_history or [],
            goal=request.goal,
            target_skills=request.target_skills or [],
        )
        final_state = await self.graph.ainvoke(initial_state)
        out = final_state.get("final_output") if isinstance(final_state, dict) else getattr(final_state, "final_output", None)
        if isinstance(out, SkillAnalysisData):
            return out
        elif isinstance(out, dict):
            return SkillAnalysisData.model_validate(out)
        raise RuntimeError("Skill analysis workflow did not return valid output.")


_skill_service: Optional[SkillService] = None


def get_skill_service() -> SkillService:
    global _skill_service
    if _skill_service is None:
        _skill_service = SkillService()
    return _skill_service
