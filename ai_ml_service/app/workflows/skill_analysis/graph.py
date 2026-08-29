"""
Skill Analysis LangGraph Workflow Graph and SkillEstimator Abstraction.
Differentiates verified assessment performance from self-reported data and computes explicit skill gaps.
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional, Tuple
from langgraph.graph import END, StateGraph
from app.llm.generation import LLMGenerationService, get_generation_service
from app.schemas.skill import SkillAnalysisData, SkillGap
from app.workflows.skill_analysis.state import SkillAnalysisWorkflowState

logger = logging.getLogger(__name__)


class SkillEstimator(ABC):
    """Abstract interface for skill estimation models."""

    @abstractmethod
    def estimate_skills(
        self,
        assessment_results: Any,
        verified_skills_input: List[Dict[str, Any]],
        self_reported_skills: Dict[str, Any],
        learning_history: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Returns (verified_scores, combined_skill_scores).
        Scores are normalized strictly between 0.0 and 1.0.
        """
        pass


class BaselineSkillEstimator(SkillEstimator):
    """
    Deterministic skill estimator.
    Calculates verified assessment percentage per skill.
    Preserves verified scores and incorporates self-reported skills with lower confidence weight.
    """

    def estimate_skills(
        self,
        assessment_results: Any,
        verified_skills_input: List[Dict[str, Any]],
        self_reported_skills: Dict[str, Any],
        learning_history: List[Dict[str, Any]],
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        verified_scores: Dict[str, float] = {}
        combined_scores: Dict[str, float] = {}

        # 1. Process explicit verified_skills_input
        for item in verified_skills_input:
            s_id = item.get("skill_id") or item.get("skill")
            score = item.get("verified_score", item.get("score", 0.0))
            if s_id:
                # Normalize 0-100 to 0.0-1.0 if needed
                score_norm = score / 100.0 if score > 1.0 else score
                verified_scores[s_id] = round(float(score_norm), 2)
                combined_scores[s_id] = round(float(score_norm), 2)

        # 2. Process assessment_results (e.g. List of questions with user_answer vs correct_answer)
        if isinstance(assessment_results, list) and len(assessment_results) > 0:
            skill_counts: Dict[str, int] = {}
            skill_correct: Dict[str, int] = {}

            for q in assessment_results:
                skill = q.get("skill_id") or q.get("skill") or "General"
                is_correct = q.get("is_correct", False)
                if not is_correct and "user_answer" in q and "correct_answer" in q:
                    is_correct = str(q["user_answer"]).strip() == str(q["correct_answer"]).strip()

                skill_counts[skill] = skill_counts.get(skill, 0) + 1
                if is_correct:
                    skill_correct[skill] = skill_correct.get(skill, 0) + 1

            for skill, count in skill_counts.items():
                v_score = round(skill_correct.get(skill, 0) / count, 2)
                verified_scores[skill] = v_score
                combined_scores[skill] = v_score
        elif isinstance(assessment_results, dict) and "score" in assessment_results:
            score_val = assessment_results["score"]
            norm_val = score_val / 100.0 if score_val > 1.0 else score_val
            target_s = assessment_results.get("skill", "Core")
            verified_scores[target_s] = round(float(norm_val), 2)
            combined_scores[target_s] = round(float(norm_val), 2)

        # 3. Process self_reported_skills (DO NOT overwrite existing verified scores)
        for s_name, raw_val in self_reported_skills.items():
            if s_name not in verified_scores:
                # Map beginner=0.3, intermediate=0.6, advanced=0.85 or numeric
                if isinstance(raw_val, str):
                    mapping = {"beginner": 0.35, "intermediate": 0.60, "advanced": 0.85, "expert": 0.95}
                    num_val = mapping.get(raw_val.lower(), 0.5)
                elif isinstance(raw_val, (int, float)):
                    num_val = raw_val / 100.0 if raw_val > 1.0 else raw_val
                else:
                    num_val = 0.5
                combined_scores[s_name] = round(float(num_val), 2)

        return verified_scores, combined_scores


def create_skill_analysis_nodes(
    generation_service: LLMGenerationService,
    skill_estimator: Optional[SkillEstimator] = None,
):
    estimator = skill_estimator or BaselineSkillEstimator()

    async def load_and_estimate_node(state: SkillAnalysisWorkflowState) -> Dict[str, Any]:
        """Node 1: Compute verified and combined skill scores."""
        logger.info(f"[{state.request_id}] Skill Analysis: Estimating skills from assessment results")
        verified, combined = estimator.estimate_skills(
            assessment_results=state.assessment_results,
            verified_skills_input=state.verified_skills_input,
            self_reported_skills=state.self_reported_skills,
            learning_history=state.learning_history,
        )

        strengths = [s for s, score in combined.items() if score >= 0.70]
        weaknesses = [s for s, score in combined.items() if score < 0.60]

        return {
            "verified_scores": verified,
            "combined_skills": combined,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "status": "scores_computed",
        }

    async def compute_skill_gaps_node(state: SkillAnalysisWorkflowState) -> Dict[str, Any]:
        """Node 2: Identify explicit skill gaps relative to target competencies."""
        targets = state.target_skills or ["Python", "Machine Learning", "Deep Learning", "MLOps"]
        gaps: List[SkillGap] = []

        for target in targets:
            current = state.combined_skills.get(target, 0.0)
            target_goal = 0.80  # Standard proficiency benchmark
            if current < target_goal:
                mag = round(target_goal - current, 2)
                priority = "high" if mag >= 0.4 else "medium"
                gaps.append(
                    SkillGap(
                        skill=target,
                        current_score=current,
                        target_score=target_goal,
                        gap_magnitude=mag,
                        priority=priority,
                    )
                )

        return {"skill_gaps": gaps, "status": "gaps_computed"}

    async def finalize_analysis_node(state: SkillAnalysisWorkflowState) -> Dict[str, Any]:
        """Node 3: Assemble structured SkillAnalysisData output."""
        estimated_levels = {k: round(v * 100, 1) for k, v in state.combined_skills.items()}
        rec_next = [g.skill for g in state.skill_gaps if g.priority == "high"]
        if not rec_next and state.skill_gaps:
            rec_next = [state.skill_gaps[0].skill]

        output = SkillAnalysisData(
            skills=state.combined_skills,
            verified_scores=state.verified_scores,
            estimated_skill_levels=estimated_levels,
            strengths=state.strengths,
            weaknesses=state.weaknesses,
            skill_gaps=state.skill_gaps,
            recommended_next_skills=rec_next,
            confidence=0.92 if len(state.verified_scores) > 0 else 0.75,
        )
        return {"final_output": output, "status": "completed"}

    return load_and_estimate_node, compute_skill_gaps_node, finalize_analysis_node


def build_skill_analysis_graph(
    generation_service: Optional[LLMGenerationService] = None,
    skill_estimator: Optional[SkillEstimator] = None,
):
    gen_svc = generation_service or get_generation_service()
    load_est, comp_gaps, finalize = create_skill_analysis_nodes(gen_svc, skill_estimator)

    workflow = StateGraph(SkillAnalysisWorkflowState)
    workflow.add_node("estimate_skills", load_est)
    workflow.add_node("compute_gaps", comp_gaps)
    workflow.add_node("finalize", finalize)

    workflow.set_entry_point("estimate_skills")
    workflow.add_edge("estimate_skills", "compute_gaps")
    workflow.add_edge("compute_gaps", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()
