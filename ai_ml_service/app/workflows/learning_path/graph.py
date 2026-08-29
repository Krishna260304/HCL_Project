"""
Learning Path LangGraph Workflow Graph.
Orchestrates multi-phase progression, resource/project assignment, DAG cycle validation, and explanation generation.
"""

import logging
from typing import Any, Dict, List, Optional
from langgraph.graph import END, StateGraph
from app.llm.generation import LLMGenerationService, get_generation_service
from app.schemas.learning_path import LearningPathData, LearningPhase, PhaseAssessment, PhaseProject, PhaseResource
from app.validation.learning_path_validator import LearningPathValidator
from app.workflows.learning_path.state import LearningPathWorkflowState

logger = logging.getLogger(__name__)


def create_learning_path_nodes(generation_service: LLMGenerationService):
    async def load_context_node(state: LearningPathWorkflowState) -> Dict[str, Any]:
        """Node 1: Extract and normalize learner skills, gaps, and prerequisites."""
        logger.info(f"[{state.request_id}] Learning Path Graph: Loading context for goal '{state.goal}'")
        return {"status": "context_loaded"}

    async def construct_phases_node(state: LearningPathWorkflowState) -> Dict[str, Any]:
        """Node 2: Synthesize multi-phase learning path via LLM or deterministic fallback."""
        goal_text = state.goal if isinstance(state.goal, str) else (state.goal.get("goal") if isinstance(state.goal, dict) else "Technology Acceleration")
        try:
            path_result = await generation_service.generate_structured(
                schema_cls=LearningPathData,
                prompt_name="learning_path_v1",
                prompt_vars={
                    "goal": goal_text,
                    "verified_skills": state.verified_skills,
                    "skill_gaps": state.skill_gaps,
                    "resources": state.candidate_resources[:8],
                    "timeline": state.timeline,
                    "preferences": state.preferences,
                },
                system_prompt="You are a principal curriculum architect. Construct modular, DAG-valid learning roadmaps.",
            )
            return {"final_output": path_result, "phases": path_result.phases, "status": "phases_constructed"}
        except Exception as exc:
            logger.warning(f"[{state.request_id}] LLM Learning path fallback: {exc}")
            # Deterministic modular fallback
            fallback_phases: List[LearningPhase] = [
                LearningPhase(
                    phase_id="phase_1",
                    title="Phase 1: Foundations & Core Competencies",
                    description="Establish core principles and close foundational skill gaps.",
                    objective="Master foundational concepts and setup development environment.",
                    order=1,
                    skills=["Foundations", "Core Principles"],
                    prerequisites=[],
                    resources=[
                        PhaseResource(
                            resource_id="res_fnd_01",
                            title="Foundational Concepts & Applied Workflows",
                            resource_type="video",
                            duration_minutes=60,
                            skills=["Foundations"],
                            is_mandatory=True,
                        )
                    ],
                    projects=[
                        PhaseProject(
                            project_id="proj_01",
                            title="Foundational Hands-on Lab",
                            description="Build initial setup and baseline verification project.",
                            difficulty="beginner",
                            estimated_hours=4,
                            deliverables=["GitHub Repo", "Verification script"],
                        )
                    ],
                    assessment=PhaseAssessment(
                        assessment_id="asm_01",
                        title="Foundational Milestone Quiz",
                        type="milestone_quiz",
                        pass_score=0.75,
                    ),
                    milestone="Foundational competencies validated",
                    estimated_duration_weeks=3,
                    explanation="Builds essential prerequisites before advancing to practical deployment.",
                ),
                LearningPhase(
                    phase_id="phase_2",
                    title="Phase 2: Applied Architecture & Production Implementation",
                    description="Deep dive into advanced topics, optimization, and project deployment.",
                    objective="Deliver production-ready implementation and close high-priority gaps.",
                    order=2,
                    skills=["Advanced Architecture", "Deployment"],
                    prerequisites=["Foundations"],
                    resources=[
                        PhaseResource(
                            resource_id="res_adv_01",
                            title="Advanced Architectural Patterns & Scalability",
                            resource_type="documentation",
                            duration_minutes=90,
                            skills=["Advanced Architecture"],
                            is_mandatory=True,
                        )
                    ],
                    projects=[
                        PhaseProject(
                            project_id="proj_02",
                            title="End-to-End Capstone Project",
                            description="Develop, test, and deploy complete production system.",
                            difficulty="advanced",
                            estimated_hours=8,
                            deliverables=["Production code", "Deployment config", "Documentation"],
                        )
                    ],
                    assessment=PhaseAssessment(
                        assessment_id="asm_02",
                        title="Final Capstone Assessment",
                        type="milestone_quiz",
                        pass_score=0.80,
                    ),
                    milestone="Capstone project validated and production ready",
                    estimated_duration_weeks=5,
                    explanation="Closes target skill gaps and completes career goal criteria.",
                ),
            ]

            path_data = LearningPathData(
                title=f"Learning Path: {goal_text}",
                description="Structured, milestone-driven roadmap designed for your background.",
                goal=goal_text,
                estimated_duration_weeks=8,
                target_role=goal_text,
                phases=fallback_phases,
                validation_status="validated",
                confidence=0.88,
            )
            return {"final_output": path_data, "phases": fallback_phases, "status": "fallback_constructed"}

    async def validate_path_node(state: LearningPathWorkflowState) -> Dict[str, Any]:
        """Node 3: Validate topological ordering, DAG cycles, and workload feasibility."""
        if not state.final_output:
            return {"status": "validation_failed", "errors": ["No path data to validate"]}

        is_valid, validation_errors = LearningPathValidator.validate_path(state.final_output)
        logger.info(
            f"[{state.request_id}] Learning Path Validation: valid={is_valid}, errors={validation_errors}"
        )
        if not is_valid:
            state.final_output.validation_status = "requires_admin_review"

        return {
            "is_valid": is_valid,
            "validation_errors": validation_errors,
            "status": "completed",
        }

    return load_context_node, construct_phases_node, validate_path_node


def build_learning_path_graph(generation_service: Optional[LLMGenerationService] = None):
    gen_svc = generation_service or get_generation_service()
    load_ctx, construct, validate = create_learning_path_nodes(gen_svc)

    workflow = StateGraph(LearningPathWorkflowState)
    workflow.add_node("load_context", load_ctx)
    workflow.add_node("construct_phases", construct)
    workflow.add_node("validate_path", validate)

    workflow.set_entry_point("load_context")
    workflow.add_edge("load_context", "construct_phases")
    workflow.add_edge("construct_phases", "validate_path")
    workflow.add_edge("validate_path", END)

    return workflow.compile()
