"""
Goal Analysis LangGraph Workflow Graph.
Orchestrates context loading, intent extraction, domain mapping, and structured validation.
"""

import logging
from typing import Any, Dict, Optional
from langgraph.graph import END, StateGraph
from app.llm.generation import LLMGenerationService, get_generation_service
from app.schemas.goal import GoalAnalysisData
from app.workflows.goal_analysis.state import GoalAnalysisWorkflowState

logger = logging.getLogger(__name__)


def create_goal_analysis_nodes(generation_service: LLMGenerationService):
    async def load_context_node(state: GoalAnalysisWorkflowState) -> Dict[str, Any]:
        """Node 1: Validate and sanitize learner context input."""
        logger.info(f"[{state.request_id}] Goal Analysis: Loading learner context")
        goal_text = state.goal.strip()
        if not goal_text:
            return {"status": "error", "errors": ["Goal description is empty"]}
        return {"status": "context_loaded", "normalized_goal": goal_text}

    async def analyze_goal_node(state: GoalAnalysisWorkflowState) -> Dict[str, Any]:
        """Node 2: Execute structured LLM goal analysis."""
        if state.status == "error":
            return {}

        logger.info(f"[{state.request_id}] Goal Analysis: Generating structured analysis for '{state.goal}'")
        try:
            result = await generation_service.generate_structured(
                schema_cls=GoalAnalysisData,
                prompt_name="goal_analysis_v1",
                prompt_vars={
                    "goal": state.goal,
                    "experience_level": state.experience_level,
                    "knowledge_areas": state.knowledge_areas,
                    "learning_history": state.learning_history,
                    "target_outcome": state.target_outcome or "Professional proficiency",
                    "timeline": state.timeline or "3-6 months",
                },
                system_prompt="You are an expert curriculum advisor. Produce structured, highly accurate goal decompositions.",
            )
            return {
                "status": "analyzed",
                "final_output": result,
                "required_domains": result.required_domains,
                "required_skills": result.required_skills,
                "possible_roles": result.possible_roles,
            }
        except Exception as exc:
            logger.error(f"[{state.request_id}] LLM Goal Analysis failed: {exc}")
            # Fallback deterministic analysis
            fallback = GoalAnalysisData(
                goal=state.goal,
                goal_type="career_advancement",
                target_outcome=state.target_outcome or "Professional competence",
                timeline=state.timeline or "3-6 months",
                required_domains=state.knowledge_areas or ["Core Foundations"],
                recommended_domains=state.knowledge_areas or ["Core Foundations"],
                required_skills=["Core Concepts", "Applied Projects"],
                possible_roles=[state.goal],
                confidence=0.75,
            )
            return {"status": "fallback_analyzed", "final_output": fallback}

    async def validate_node(state: GoalAnalysisWorkflowState) -> Dict[str, Any]:
        """Node 3: Validate output structure."""
        if not state.final_output:
            return {"status": "failed", "errors": ["No goal analysis output produced"]}
        return {"status": "completed"}

    return load_context_node, analyze_goal_node, validate_node


def build_goal_analysis_graph(generation_service: Optional[LLMGenerationService] = None):
    gen_svc = generation_service or get_generation_service()
    load_ctx, analyze_goal, validate = create_goal_analysis_nodes(gen_svc)

    workflow = StateGraph(GoalAnalysisWorkflowState)
    workflow.add_node("load_context", load_ctx)
    workflow.add_node("analyze_goal", analyze_goal)
    workflow.add_node("validate", validate)

    workflow.set_entry_point("load_context")
    workflow.add_edge("load_context", "analyze_goal")
    workflow.add_edge("analyze_goal", "validate")
    workflow.add_edge("validate", END)

    return workflow.compile()
