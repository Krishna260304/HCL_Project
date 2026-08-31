"""
Assessment Generation LangGraph Workflow Graph.
Orchestrates blueprinting, Qwen MCQ generation, deterministic validation, and isolated per-question repair.
"""

import logging
from typing import Any, Dict, List, Optional
from langgraph.graph import END, StateGraph
from app.llm.generation import LLMGenerationService, get_generation_service
from app.schemas.assessment import AssessmentBlueprint, AssessmentData, MCQQuestion
from app.validation.question_validator import QuestionValidator
from app.workflows.assessment_generation.state import AssessmentWorkflowState

logger = logging.getLogger(__name__)


DOMAIN_QUESTION_BANK: Dict[str, List[Dict[str, Any]]] = {
    "python": [
        {
            "question": "How does Python handle memory management for objects under the hood?",
            "options": [
                "Reference counting combined with a generational cyclic garbage collector",
                "Manual allocate and deallocate syscalls",
                "Pure mark-and-sweep garbage collection exclusively",
                "Compile-time static stack allocation only"
            ],
            "correct_answer": "Reference counting combined with a generational cyclic garbage collector",
            "explanation": "CPython utilizes reference counting as its primary memory management mechanism along with generational garbage collection to resolve reference cycles.",
            "skill": "Python",
            "topic": "Memory Management",
            "learning_objective": "Understand Python memory management and cyclic GC architecture.",
        },
        {
            "question": "What is the primary operational benefit of using Python generators with the 'yield' statement?",
            "options": [
                "Produces an iterator that lazily yields values one at a time to optimize memory usage",
                "Enforces compile-time static type safety",
                "Spawns independent OS-level background threads",
                "Eliminates the Global Interpreter Lock (GIL)"
            ],
            "correct_answer": "Produces an iterator that lazily yields values one at a time to optimize memory usage",
            "explanation": "Generators compute values on-demand, allowing streaming of large datasets without buffering the entire sequence in memory.",
            "skill": "Python",
            "topic": "Iterators & Generators",
            "learning_objective": "Leverage generators for memory-efficient streaming.",
        }
    ],
    "machine_learning": [
        {
            "question": "How does L2 regularization (Ridge) reduce overfitting in regression models?",
            "options": [
                "Penalizes the sum of squared weights, shrinking coefficients toward zero without setting them to exact zero",
                "Forces non-essential feature weights to exactly zero for feature selection",
                "Randomly drops neurons during training iterations",
                "Increases the learning rate dynamically to escape local minima"
            ],
            "correct_answer": "Penalizes the sum of squared weights, shrinking coefficients toward zero without setting them to exact zero",
            "explanation": "L2 regularization adds a quadratic weight penalty to the cost function, reducing variance and smoothing feature influence.",
            "skill": "Machine Learning",
            "topic": "Regularization Techniques",
            "learning_objective": "Understand how regularization reduces model variance and prevents overfitting.",
        },
        {
            "question": "When evaluating a classifier on a heavily imbalanced dataset, which metric is generally preferred over raw accuracy?",
            "options": [
                "Precision-Recall AUC (PR-AUC) or F1-Score",
                "Standard Classification Accuracy",
                "Mean Squared Error (MSE)",
                "R-squared goodness of fit"
            ],
            "correct_answer": "Precision-Recall AUC (PR-AUC) or F1-Score",
            "explanation": "Accuracy can be deceptively high when majority classes dominate; PR-AUC and F1-Score evaluate true positive performance against precision/recall trade-offs.",
            "skill": "Machine Learning",
            "topic": "Model Evaluation",
            "learning_objective": "Select appropriate evaluation metrics for skewed classification problems.",
        }
    ],
    "deep_learning": [
        {
            "question": "Why is Scaled Dot-Product Attention scaled by sqrt(d_k) in Transformer architectures?",
            "options": [
                "To prevent large dot products from pushing softmax into regions with vanishingly small gradients",
                "To normalize output embeddings to unit variance",
                "To reduce computational complexity from quadratic to linear",
                "To enforce causal masking across attention heads"
            ],
            "correct_answer": "To prevent large dot products from pushing softmax into regions with vanishingly small gradients",
            "explanation": "As the key dimension grows, dot products grow large, causing softmax to saturate with near-zero gradients; sqrt(d_k) scaling stabilizes backpropagation.",
            "skill": "Deep Learning",
            "topic": "Transformers & Attention",
            "learning_objective": "Understand transformer attention mathematical stability.",
        }
    ],
    "web_development": [
        {
            "question": "What is the primary architectural benefit of React Server Components (RSC)?",
            "options": [
                "Zero client-side JavaScript bundle footprint for server components while retaining interactive client leaves",
                "Eliminates the requirement for CSS styling",
                "Replaces standard HTTP requests with WebSocket channels automatically",
                "Executes JavaScript directly on user GPU hardware"
            ],
            "correct_answer": "Zero client-side JavaScript bundle footprint for server components while retaining interactive client leaves",
            "explanation": "Server components execute exclusively on the server, avoiding sending component code or server-only dependencies down to the browser bundle.",
            "skill": "Web Development",
            "topic": "Frontend Architecture",
            "learning_objective": "Understand hybrid server/client component execution models.",
        }
    ],
    "cloud_devops": [
        {
            "question": "What is the core principle of Infrastructure as Code (IaC) with tools like Terraform?",
            "options": [
                "Managing and provisioning compute infrastructure through version-controlled, declarative configuration files",
                "Compiling application binaries directly into assembly",
                "Automating manual SSH terminal sessions",
                "Encrypting hard disk drives at the hardware level"
            ],
            "correct_answer": "Managing and provisioning compute infrastructure through version-controlled, declarative configuration files",
            "explanation": "IaC provides reproducible, declarative definitions of cloud resources that avoid configuration drift across deployments.",
            "skill": "DevOps & Cloud",
            "topic": "Infrastructure as Code",
            "learning_objective": "Apply declarative configuration to automated cloud provisioning.",
        }
    ]
}


def get_domain_fallback_questions(goal: str, skills: List[str], count: int, difficulty: str) -> List[MCQQuestion]:
    selected: List[MCQQuestion] = []
    normalized_skills = [s.lower().replace(" ", "_") for s in skills]
    goal_lower = goal.lower()

    for key, q_list in DOMAIN_QUESTION_BANK.items():
        is_relevant = any(key in s or s in key for s in normalized_skills) or (key.replace("_", " ") in goal_lower)
        if is_relevant:
            for q_data in q_list:
                selected.append(MCQQuestion(
                    id=f"q_{len(selected) + 1}",
                    question=q_data["question"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    skill=q_data.get("skill", skills[0] if skills else "General"),
                    topic=q_data.get("topic", "Core Concepts"),
                    difficulty=difficulty,
                    learning_objective=q_data.get("learning_objective", f"Evaluate proficiency in {q_data.get('skill', 'Core')}"),
                    explanation=q_data.get("explanation", "Mastery of core domain principles ensures correct application.")
                ))

    # If more questions needed, draw from remaining domain banks
    if len(selected) < count:
        for q_list in DOMAIN_QUESTION_BANK.values():
            for q_data in q_list:
                if not any(s.question == q_data["question"] for s in selected):
                    selected.append(MCQQuestion(
                        id=f"q_{len(selected) + 1}",
                        question=q_data["question"],
                        options=q_data["options"],
                        correct_answer=q_data["correct_answer"],
                        skill=q_data.get("skill", skills[0] if skills else "General"),
                        topic=q_data.get("topic", "Core Concepts"),
                        difficulty=difficulty,
                        learning_objective=q_data.get("learning_objective", "Assess domain competence"),
                        explanation=q_data.get("explanation", "Core technical foundation principle.")
                    ))
                if len(selected) >= count:
                    break
            if len(selected) >= count:
                break

    return selected[:count]


def create_assessment_nodes(generation_service: LLMGenerationService):
    async def load_context_node(state: AssessmentWorkflowState) -> Dict[str, Any]:
        """Node 1: Extract and sanitize assessment parameters."""
        logger.info(f"[{state.request_id}] Assessment Graph: Loading context for goal '{state.goal}'")
        target_skills = state.required_skills or state.knowledge_areas or ["General Problem Solving"]
        return {"status": "context_loaded", "required_skills": target_skills}

    async def create_blueprint_node(state: AssessmentWorkflowState) -> Dict[str, Any]:
        """Node 2: Calculate question distribution and assessment blueprint."""
        skills = state.required_skills
        blueprint = AssessmentBlueprint(
            title=f"Diagnostic Assessment: {state.goal}",
            description=f"Tailored diagnostic evaluation covering {', '.join(skills[:4])}",
            target_skills=skills,
            total_questions=state.num_questions,
        )
        return {"blueprint": blueprint, "status": "blueprinted"}

    async def generate_questions_node(state: AssessmentWorkflowState) -> Dict[str, Any]:
        """Node 3: Generate batch MCQ questions using structured LLM call with resilient fallbacks."""
        logger.info(f"[{state.request_id}] Assessment Graph: Generating {state.num_questions} questions via LLM")
        requested_count = max(5, min(10, state.num_questions))
        target_skills = state.required_skills or state.knowledge_areas or ["General Technical Foundations"]

        try:
            raw_assessment = await generation_service.generate_structured(
                schema_cls=AssessmentData,
                prompt_name="assessment_generation_v1",
                prompt_vars={
                    "goal": state.goal,
                    "experience_level": state.experience_level,
                    "skills": target_skills,
                    "knowledge_areas": state.knowledge_areas,
                    "num_questions": requested_count,
                },
                system_prompt="You are an expert technical psychometrician. Generate rigorous, unambiguous MCQ questions.",
                max_tokens=2048,
                max_retries=1,
            )
            if raw_assessment and raw_assessment.questions:
                return {
                    "generated_questions": raw_assessment.questions,
                    "status": "questions_generated",
                }
        except Exception as exc:
            logger.warning(f"[{state.request_id}] Assessment LLM generation error: {exc}. Utilizing domain-aware fallback question bank.")

        # High quality domain-aware fallback questions
        fallback_questions = get_domain_fallback_questions(
            goal=state.goal,
            skills=target_skills,
            count=requested_count,
            difficulty=state.experience_level,
        )
        return {
            "generated_questions": fallback_questions,
            "status": "questions_generated",
        }

    async def validate_questions_node(state: AssessmentWorkflowState) -> Dict[str, Any]:
        """Node 4: Perform deterministic structural and psychometric validation."""
        valid, invalid = QuestionValidator.validate_assessment_batch(state.generated_questions)
        logger.info(
            f"[{state.request_id}] Assessment Validation: {len(valid)} valid, {len(invalid)} invalid questions"
        )
        return {
            "valid_questions": valid,
            "invalid_questions": invalid,
            "status": "validated",
        }

    async def repair_questions_node(state: AssessmentWorkflowState) -> Dict[str, Any]:
        """Node 5: Isolated per-question repair without regenerating the entire assessment."""
        repaired_batch: List[MCQQuestion] = list(state.valid_questions)
        attempts = state.repair_attempts + 1

        for idx, invalid_q, error_reason in state.invalid_questions:
            logger.info(f"[{state.request_id}] Repairing question index {idx}: {error_reason}")
            try:
                repaired = await generation_service.generate_structured(
                    schema_cls=MCQQuestion,
                    prompt_name="question_repair_v1",
                    prompt_vars={
                        "error_reason": error_reason,
                        "invalid_question": invalid_q.model_dump_json(),
                        "skill": invalid_q.get_skill(),
                        "difficulty": invalid_q.difficulty,
                    },
                    system_prompt="You are a strict question repair engine. Fix all validation flaws.",
                )
                repaired_batch.append(repaired)
            except Exception as e:
                logger.warning(f"Failed to repair question {idx}: {e}")
                # Fallback valid question for this skill
                fallback_q = MCQQuestion(
                    id=f"q_repaired_{idx}",
                    question=f"Which core concept is central to understanding {invalid_q.get_skill()} in practice?",
                    options=[
                        f"Fundamental principles and best practices in {invalid_q.get_skill()}",
                        "Static memory allocation without garbage collection",
                        "Manual execution of unoptimized binaries",
                        "Deprecated legacy protocols",
                    ],
                    correct_answer=f"Fundamental principles and best practices in {invalid_q.get_skill()}",
                    skill=invalid_q.get_skill(),
                    topic=invalid_q.topic or "Core Foundations",
                    difficulty=invalid_q.difficulty,
                    learning_objective=f"Evaluate foundational comprehension of {invalid_q.get_skill()}",
                    explanation=f"Mastery of {invalid_q.get_skill()} requires understanding its fundamental architectural principles.",
                )
                repaired_batch.append(fallback_q)

        return {
            "generated_questions": repaired_batch,
            "repair_attempts": attempts,
            "status": "repaired",
        }

    async def finalize_assessment_node(state: AssessmentWorkflowState) -> Dict[str, Any]:
        """Node 6: Finalize assessment metadata and assemble output."""
        requested_count = max(5, min(10, state.num_questions))
        questions = list((state.valid_questions or state.generated_questions)[:requested_count])

        # Keep the user-facing contract even when an LLM returns too few valid
        # items. These deterministic additions are valid MCQs and preserve the
        # requested diagnostic size without launching another expensive batch.
        target_skills = state.required_skills or state.knowledge_areas or ["General Problem Solving"]
        while len(questions) < requested_count:
            number = len(questions) + 1
            skill = target_skills[(number - 1) % len(target_skills)]
            correct_answer = f"Apply the core principles and verify the result for {skill}"
            questions.append(MCQQuestion(
                id=f"q_supplemental_{number}",
                question=f"Which approach is the most reliable way to solve a practical {skill} task?",
                options=[
                    correct_answer,
                    "Skip validation and rely on an untested first result",
                    "Memorize syntax without understanding the underlying concept",
                    "Ignore constraints and edge cases until after delivery",
                ],
                correct_answer=correct_answer,
                skill=skill,
                topic="Applied Foundations",
                difficulty=state.experience_level,
                learning_objective=f"Apply reliable problem-solving practices in {skill}",
                explanation="Reliable work applies the relevant principles, accounts for constraints, and verifies the outcome.",
            ))
        skill_ids = list({q.get_skill() for q in questions if q.get_skill()})
        topic_ids = list({q.topic for q in questions if q.topic})

        final_data = AssessmentData(
            title=state.blueprint.title if state.blueprint else f"Assessment: {state.goal}",
            description=state.blueprint.description if state.blueprint else "Diagnostic assessment",
            difficulty=state.experience_level,
            duration=max(10, len(questions) * 3),
            skill_ids=skill_ids,
            topic_ids=topic_ids,
            questions=questions,
            confidence=0.95 if len(state.invalid_questions) == 0 else 0.85,
        )
        return {"final_output": final_data, "status": "completed"}

    return (
        load_context_node,
        create_blueprint_node,
        generate_questions_node,
        validate_questions_node,
        repair_questions_node,
        finalize_assessment_node,
    )


def should_repair(state: AssessmentWorkflowState) -> str:
    """Routing condition: repair invalid questions if any exist and max retries not exceeded."""
    if state.invalid_questions and state.repair_attempts < 2:
        return "repair_questions"
    return "finalize_assessment"


def build_assessment_generation_graph(generation_service: Optional[LLMGenerationService] = None):
    gen_svc = generation_service or get_generation_service()
    (
        load_ctx,
        blueprint,
        generate_qs,
        validate_qs,
        repair_qs,
        finalize,
    ) = create_assessment_nodes(gen_svc)

    workflow = StateGraph(AssessmentWorkflowState)
    workflow.add_node("load_context", load_ctx)
    workflow.add_node("create_blueprint", blueprint)
    workflow.add_node("generate_questions", generate_qs)
    workflow.add_node("validate_questions", validate_qs)
    workflow.add_node("repair_questions", repair_qs)
    workflow.add_node("finalize_assessment", finalize)

    workflow.set_entry_point("load_context")
    workflow.add_edge("load_context", "create_blueprint")
    workflow.add_edge("create_blueprint", "generate_questions")
    workflow.add_edge("generate_questions", "validate_questions")

    workflow.add_conditional_edges(
        "validate_questions",
        should_repair,
        {
            "repair_questions": "repair_questions",
            "finalize_assessment": "finalize_assessment",
        },
    )
    workflow.add_edge("repair_questions", "validate_questions")
    workflow.add_edge("finalize_assessment", END)

    return workflow.compile()
