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

def get_domain_fallback_learning_path(goal_text: str, skills_dict: Dict[str, float], timeline: str) -> LearningPathData:
    goal_lower = goal_text.lower()
    skills_list = list(skills_dict.keys()) if skills_dict else ["Core Concepts"]

    if any(k in goal_lower for k in ["machine learning", "ml", "ai", "deep learning", "data science"]):
        phases = [
            LearningPhase(
                phase_id="phase_1",
                title="Phase 1: Mathematical Foundations & Data Pipelines",
                description="Consolidate Python numerical computing, linear algebra, vectorization, and data ingestion pipelines.",
                objective=f"Master core statistical foundations and build robust preprocessing workflows for {goal_text}.",
                order=1,
                skills=["Python", "NumPy", "Pandas", "Linear Algebra", "Data Cleaning"],
                prerequisites=[],
                resources=[
                    PhaseResource(
                        resource_id="res_ml_01",
                        title="Numerical Computing & Vectorized Data Pipelines with NumPy/Pandas",
                        resource_type="video",
                        duration_minutes=60,
                        skills=["Python", "NumPy"],
                        is_mandatory=True,
                    ),
                    PhaseResource(
                        resource_id="res_ml_02",
                        title="Essential Mathematics & Statistical Modeling for ML",
                        resource_type="documentation",
                        duration_minutes=90,
                        skills=["Linear Algebra", "Statistics"],
                        is_mandatory=True,
                    ),
                ],
                projects=[
                    PhaseProject(
                        project_id="proj_ml_01",
                        title="Automated Feature Engineering & Preprocessing Pipeline",
                        description="Construct an end-to-end data pipeline with validation schemas and baseline estimators.",
                        difficulty="beginner",
                        estimated_hours=6,
                        deliverables=["Data Pipeline Module", "Unit Tests", "EDA Notebook"],
                    )
                ],
                assessment=PhaseAssessment(
                    assessment_id="asm_ml_01",
                    title="Mathematical Foundations & Preprocessing Assessment",
                    type="milestone_quiz",
                    pass_score=0.75,
                ),
                milestone="Core data pipelines and baseline modelling validated",
                estimated_duration_weeks=3,
                explanation="Establishes prerequisite mathematical and preprocessing rigor before architectural modeling.",
            ),
            LearningPhase(
                phase_id="phase_2",
                title="Phase 2: Deep Learning Architecture & Model Training",
                description="Train deep neural networks, implement Transformer attention mechanisms, and optimize loss functions.",
                objective="Build, train, and fine-tune production-grade deep learning models using PyTorch/TensorFlow.",
                order=2,
                skills=["PyTorch", "TensorFlow", "Deep Learning", "Transformers", "Hyperparameter Tuning"],
                prerequisites=["Phase 1: Mathematical Foundations & Data Pipelines"],
                resources=[
                    PhaseResource(
                        resource_id="res_ml_03",
                        title="PyTorch Deep Learning & Transformer Architectures in Practice",
                        resource_type="video",
                        duration_minutes=90,
                        skills=["PyTorch", "Transformers"],
                        is_mandatory=True,
                    ),
                    PhaseResource(
                        resource_id="res_ml_04",
                        title="Model Evaluation, Loss Stabilization & Regularization Techniques",
                        resource_type="documentation",
                        duration_minutes=75,
                        skills=["Deep Learning", "Optimization"],
                        is_mandatory=True,
                    ),
                ],
                projects=[
                    PhaseProject(
                        project_id="proj_ml_02",
                        title="Domain Transformer & Transfer Learning Benchmark",
                        description="Implement custom fine-tuning pipeline with mixed-precision training and evaluation benchmarks.",
                        difficulty="intermediate",
                        estimated_hours=10,
                        deliverables=["PyTorch Model", "Training Loop Script", "Evaluation Report"],
                    )
                ],
                assessment=PhaseAssessment(
                    assessment_id="asm_ml_02",
                    title="Deep Learning & Transformer Architecture Evaluation",
                    type="milestone_quiz",
                    pass_score=0.75,
                ),
                milestone="Deep learning architecture trained and benchmarked",
                estimated_duration_weeks=3,
                explanation="Develops core competency in modern model architectures and loss optimization.",
            ),
            LearningPhase(
                phase_id="phase_3",
                title="Phase 3: MLOps, Model Serving & Production Deployment",
                description="Package models with ONNX/TorchScript, serve low-latency inference endpoints, and set up drift monitoring.",
                objective=f"Deploy an enterprise-ready, scalable AI service demonstrating complete end-to-end readiness for {goal_text}.",
                order=3,
                skills=["MLOps", "Model Serving", "Docker", "FastAPI", "Monitoring & Drift"],
                prerequisites=["Phase 2: Deep Learning Architecture & Model Training"],
                resources=[
                    PhaseResource(
                        resource_id="res_ml_05",
                        title="Production ML Inference, Containerization & CI/CD Pipelines",
                        resource_type="documentation",
                        duration_minutes=80,
                        skills=["MLOps", "Docker"],
                        is_mandatory=True,
                    ),
                ],
                projects=[
                    PhaseProject(
                        project_id="proj_ml_03",
                        title=f"{goal_text} Production Capstone Service",
                        description="Deploy containerized model service with async endpoints, caching, rate limiting, and telemetry.",
                        difficulty="advanced",
                        estimated_hours=14,
                        deliverables=["Microservice Code", "Dockerfile & Compose", "Live API Docs", "CI/CD Pipeline"],
                    )
                ],
                assessment=PhaseAssessment(
                    assessment_id="asm_ml_03",
                    title="MLOps & Production Deployment Certification",
                    type="milestone_quiz",
                    pass_score=0.80,
                ),
                milestone="Full production capstone system deployed and operational",
                estimated_duration_weeks=3,
                explanation="Validates industry readiness and production deployment mastery.",
            ),
        ]
    else:
        # General Software Engineering / Web / Cloud Roadmap
        phases = [
            LearningPhase(
                phase_id="phase_1",
                title="Phase 1: Foundations & Architecture Baseline",
                description=f"Establish development environment, core language syntax, and design patterns for {goal_text}.",
                objective="Master foundational principles and establish a modern development toolchain.",
                order=1,
                skills=skills_list[:3] if skills_list else ["Core Foundations", "Version Control"],
                prerequisites=[],
                resources=[
                    PhaseResource(
                        resource_id="res_gen_01",
                        title=f"{goal_text} Architectural Fundamentals & Toolchains",
                        resource_type="video",
                        duration_minutes=60,
                        skills=skills_list[:2] if skills_list else ["Foundations"],
                        is_mandatory=True,
                    ),
                ],
                projects=[
                    PhaseProject(
                        project_id="proj_gen_01",
                        title="Foundational Architecture Prototype",
                        description="Implement modular baseline application with automated testing and structured schemas.",
                        difficulty="beginner",
                        estimated_hours=6,
                        deliverables=["Code Repository", "Test Suite", "Setup Guide"],
                    )
                ],
                assessment=PhaseAssessment(
                    assessment_id="asm_gen_01",
                    title="Foundational Competency Assessment",
                    type="milestone_quiz",
                    pass_score=0.75,
                ),
                milestone="Foundational competencies validated",
                estimated_duration_weeks=3,
                explanation="Ensures solid architectural grounding before advancing to complex subsystems.",
            ),
            LearningPhase(
                phase_id="phase_2",
                title="Phase 2: Core Engineering & Systems Implementation",
                description="Build scalable subsystems, integrate asynchronous workflows, and optimize data persistence.",
                objective="Implement production-grade business logic and solve complex integration challenges.",
                order=2,
                skills=["System Design", "Database Optimization", "Async Processing"],
                prerequisites=["Phase 1: Foundations & Architecture Baseline"],
                resources=[
                    PhaseResource(
                        resource_id="res_gen_02",
                        title="Advanced System Design & High-Throughput Engineering",
                        resource_type="documentation",
                        duration_minutes=90,
                        skills=["System Design"],
                        is_mandatory=True,
                    ),
                ],
                projects=[
                    PhaseProject(
                        project_id="proj_gen_02",
                        title="Interactive Applied System Project",
                        description="Construct robust modular service with caching, transaction isolation, and integration tests.",
                        difficulty="intermediate",
                        estimated_hours=10,
                        deliverables=["Modular Service", "Integration Tests", "API Specs"],
                    )
                ],
                assessment=PhaseAssessment(
                    assessment_id="asm_gen_02",
                    title="Applied Engineering & System Design Assessment",
                    type="milestone_quiz",
                    pass_score=0.75,
                ),
                milestone="Core systems implementation validated",
                estimated_duration_weeks=3,
                explanation="Develops real-world engineering proficiency.",
            ),
            LearningPhase(
                phase_id="phase_3",
                title="Phase 3: Production Deployment & Capstone Portfolio",
                description="Containerize services, configure CI/CD pipelines, and deploy highly available capstone to production.",
                objective=f"Deliver production-grade capstone project demonstrating end-to-end readiness for {goal_text}.",
                order=3,
                skills=["Cloud Deployment", "CI/CD", "Monitoring", "Security & Reliability"],
                prerequisites=["Phase 2: Core Engineering & Systems Implementation"],
                resources=[
                    PhaseResource(
                        resource_id="res_gen_03",
                        title="Cloud Infrastructure, Container Orchestration & Observability",
                        resource_type="documentation",
                        duration_minutes=75,
                        skills=["Cloud Deployment", "CI/CD"],
                        is_mandatory=True,
                    ),
                ],
                projects=[
                    PhaseProject(
                        project_id="proj_gen_03",
                        title=f"{goal_text} Production Capstone",
                        description="Deploy full production application with automated pipelines, monitoring, and live documentation.",
                        difficulty="advanced",
                        estimated_hours=14,
                        deliverables=["Live Cloud Deployment", "CI/CD Workflows", "Architecture Documentation"],
                    )
                ],
                assessment=PhaseAssessment(
                    assessment_id="asm_gen_03",
                    title="Final Capstone Certification Exam",
                    type="milestone_quiz",
                    pass_score=0.80,
                ),
                milestone="Capstone portfolio complete and verified production-ready",
                estimated_duration_weeks=3,
                explanation="Demonstrates professional mastery and production readiness.",
            ),
        ]

    return LearningPathData(
        title=f"Personalized Learning Path: {goal_text}",
        description=f"Curated, milestone-driven curriculum mapped to your verified competency profile and career destination as {goal_text}.",
        goal=goal_text,
        estimated_duration_weeks=9,
        target_role=goal_text,
        phases=phases,
        validation_status="validated",
        confidence=0.95,
    )


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
                    "timeline": state.timeline or "9 weeks",
                },
                system_prompt="You are a principal curriculum architect. Construct modular, sequential learning roadmaps.",
                max_tokens=2048,
                max_retries=1,
            )
            if path_result and path_result.phases and len(path_result.phases) >= 2:
                return {"final_output": path_result, "phases": path_result.phases, "status": "phases_constructed"}
        except Exception as exc:
            logger.warning(f"[{state.request_id}] LLM Learning path fallback: {exc}")

        # Deterministic domain-tailored fallback
        path_data = get_domain_fallback_learning_path(
            goal_text=goal_text,
            skills_dict=state.verified_skills if isinstance(state.verified_skills, dict) else {},
            timeline=state.timeline or "9 weeks",
        )
        return {"final_output": path_data, "phases": path_data.phases, "status": "fallback_constructed"}

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
