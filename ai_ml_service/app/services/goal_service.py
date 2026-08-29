"""
Goal Analysis Service.
"""

from typing import Optional
from app.schemas.goal import GoalAnalysisData, GoalAnalysisRequest
from app.utils.ids import generate_request_id
from app.workflows.goal_analysis.graph import build_goal_analysis_graph
from app.workflows.goal_analysis.state import GoalAnalysisWorkflowState


class GoalService:
    def __init__(self):
        self.graph = build_goal_analysis_graph()

    async def analyze(self, request: GoalAnalysisRequest) -> GoalAnalysisData:
        req_id = request.request_id or generate_request_id()
        initial_state = GoalAnalysisWorkflowState(
            request_id=req_id,
            user_id=request.user_id,
            goal=request.get_goal_text(),
            learner_profile=request.learner_profile or {},
            knowledge_areas=request.knowledge_areas or [],
            experience_level=request.experience_level or "intermediate",
            learning_history=request.learning_history or [],
            target_outcome=request.target_outcome,
            timeline=request.timeline,
        )
        final_state = await self.graph.ainvoke(initial_state)
        # In langgraph, if state is returned as a dict or object
        out = final_state.get("final_output") if isinstance(final_state, dict) else getattr(final_state, "final_output", None)
        if isinstance(out, GoalAnalysisData):
            return out
        elif isinstance(out, dict):
            return GoalAnalysisData.model_validate(out)
        raise RuntimeError("Goal analysis workflow did not return a valid output.")


_goal_service: Optional[GoalService] = None


def get_goal_service() -> GoalService:
    global _goal_service
    if _goal_service is None:
        _goal_service = GoalService()
    return _goal_service
