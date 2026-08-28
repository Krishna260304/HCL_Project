"""
Assessment Generation Service.
"""

from typing import Optional
from app.schemas.assessment import AssessmentData, AssessmentGenerationRequest
from app.utils.ids import generate_request_id
from app.workflows.assessment_generation.graph import build_assessment_generation_graph
from app.workflows.assessment_generation.state import AssessmentWorkflowState


class AssessmentService:
    def __init__(self):
        self.graph = build_assessment_generation_graph()

    async def generate(self, request: AssessmentGenerationRequest) -> AssessmentData:
        req_id = request.request_id or generate_request_id()
        goal_text = request.goal if isinstance(request.goal, str) else (request.goal.get("goal") if isinstance(request.goal, dict) else "Technology")
        initial_state = AssessmentWorkflowState(
            request_id=req_id,
            goal=str(goal_text),
            experience_level=request.experience_level or "intermediate",
            knowledge_areas=request.knowledge_areas or [],
            self_reported_skills=request.self_reported_skills or {},
            learning_history=request.learning_history or [],
            required_skills=request.required_skills or request.skills or [],
            num_questions=request.num_questions or 5,
        )
        final_state = await self.graph.ainvoke(initial_state)
        out = final_state.get("final_output") if isinstance(final_state, dict) else getattr(final_state, "final_output", None)
        if isinstance(out, AssessmentData):
            return out
        elif isinstance(out, dict):
            return AssessmentData.model_validate(out)
        raise RuntimeError("Assessment workflow did not return valid assessment data.")


_assessment_service: Optional[AssessmentService] = None


def get_assessment_service() -> AssessmentService:
    global _assessment_service
    if _assessment_service is None:
        _assessment_service = AssessmentService()
    return _assessment_service
