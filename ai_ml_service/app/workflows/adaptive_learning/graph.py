"""
Adaptive Learning LangGraph Workflow Graph.
Orchestrates dynamic skill updates, remedial intervention insertion, and learning roadmap adjustments.
"""

import logging
from typing import Any, Dict, List, Optional
from langgraph.graph import END, StateGraph
from app.llm.generation import LLMGenerationService, get_generation_service
from app.retrieval.reranker import ResourceRanker, get_resource_ranker
from app.schemas.recommendation import RecommendationEvidence, RecommendationItem
from app.schemas.skill import SkillGap
from app.workflows.adaptive_learning.state import AdaptiveLearningWorkflowState

logger = logging.getLogger(__name__)


def create_adaptive_learning_nodes(
    generation_service: LLMGenerationService,
    resource_ranker: ResourceRanker,
):
    async def evaluate_performance_node(state: AdaptiveLearningWorkflowState) -> Dict[str, Any]:
        """Node 1: Compute updated skill scores from new assessment performance."""
        logger.info(f"[{state.request_id}] Adaptive Learning: Evaluating latest assessment results")
        updated = dict(state.current_skill_scores)

        # Ingest latest assessment scores
        assessment_data = state.latest_assessment
        if "score" in assessment_data:
            s_name = assessment_data.get("skill") or assessment_data.get("topic", "General")
            raw_score = float(assessment_data["score"])
            norm_score = raw_score / 100.0 if raw_score > 1.0 else raw_score
            # Exponential moving average update (60% weight to new performance)
            old_score = updated.get(s_name, 0.5)
            updated[s_name] = round(0.4 * old_score + 0.6 * norm_score, 2)
        elif "skills" in assessment_data and isinstance(assessment_data["skills"], dict):
            for s_name, score_val in assessment_data["skills"].items():
                s_score = float(score_val)
                norm_score = s_score / 100.0 if s_score > 1.0 else s_score
                old_score = updated.get(s_name, 0.5)
                updated[s_name] = round(0.4 * old_score + 0.6 * norm_score, 2)

        return {"updated_skill_scores": updated, "status": "scores_updated"}

    async def determine_adaptations_node(state: AdaptiveLearningWorkflowState) -> Dict[str, Any]:
        """Node 2: Identify topics requiring remediation or fast-tracking."""
        path_changes: List[Dict[str, Any]] = []
        new_gaps: List[SkillGap] = []
        reasons: List[str] = []
        adjust_roadmap = False
        re_rank = False

        for skill, score in state.updated_skill_scores.items():
            if score < 0.60:
                # Skill gap identified - remedial intervention required
                gap_mag = round(0.80 - score, 2)
                new_gaps.append(
                    SkillGap(
                        skill=skill,
                        current_score=score,
                        target_score=0.80,
                        gap_magnitude=gap_mag,
                        priority="high",
                    )
                )
                path_changes.append({
                    "action": "insert_remedial_module",
                    "skill": skill,
                    "reason": f"Assessment score on {skill} ({score * 100:.0f}%) is below proficiency threshold.",
                    "priority": "high",
                })
                reasons.append(f"Inserted targeted remedial practice for {skill} (current score {score * 100:.0f}%).")
                adjust_roadmap = True
                re_rank = True
            elif score >= 0.80:
                path_changes.append({
                    "action": "mark_competency_mastered",
                    "skill": skill,
                    "reason": f"Demonstrated high mastery ({score * 100:.0f}%). Fast-tracking to advanced topics.",
                })
                reasons.append(f"Marked {skill} as mastered ({score * 100:.0f}%). Fast-tracking roadmap.")

        if not path_changes:
            reasons.append("Steady learning progression verified. No roadmap alteration needed.")

        return {
            "new_skill_gaps": new_gaps,
            "path_changes": path_changes,
            "reason": " ".join(reasons),
            "adjust_roadmap": adjust_roadmap,
            "re_rank_resources": re_rank,
            "status": "adaptations_determined",
        }

    async def generate_remedial_recommendations_node(state: AdaptiveLearningWorkflowState) -> Dict[str, Any]:
        """Node 3: Formulate remedial recommendation items."""
        recs: List[RecommendationItem] = []
        for gap in state.new_skill_gaps:
            evidence = RecommendationEvidence(
                skill_gap_match=gap.gap_magnitude,
                prerequisite_satisfied=True,
                difficulty_aligned=True,
                matched_skills=[gap.skill],
                missing_skills=[],
                quality_score=0.90,
            )
            recs.append(
                RecommendationItem(
                    resource_id=f"remedial_{gap.skill.lower().replace(' ', '_')}",
                    title=f"Targeted Remedial Practice: {gap.skill}",
                    skill_id=gap.skill,
                    score=0.92,
                    reason=f"Recommended remedial refresher to reinforce {gap.skill} following recent assessment.",
                    source="adaptive_engine",
                    matched_skills=[gap.skill],
                    difficulty_match="optimal",
                    prerequisite_status="satisfied",
                    evidence=evidence,
                )
            )

        return {"new_recommendations": recs, "status": "completed"}

    return evaluate_performance_node, determine_adaptations_node, generate_remedial_recommendations_node


def build_adaptive_learning_graph(
    generation_service: Optional[LLMGenerationService] = None,
    resource_ranker: Optional[ResourceRanker] = None,
):
    gen_svc = generation_service or get_generation_service()
    ranker = resource_ranker or get_resource_ranker()

    eval_node, adapt_node, recs_node = create_adaptive_learning_nodes(gen_svc, ranker)

    workflow = StateGraph(AdaptiveLearningWorkflowState)
    workflow.add_node("evaluate_performance", eval_node)
    workflow.add_node("determine_adaptations", adapt_node)
    workflow.add_node("generate_remedial_recommendations", recs_node)

    workflow.set_entry_point("evaluate_performance")
    workflow.add_edge("evaluate_performance", "determine_adaptations")
    workflow.add_edge("determine_adaptations", "generate_remedial_recommendations")
    workflow.add_edge("generate_remedial_recommendations", END)

    return workflow.compile()
