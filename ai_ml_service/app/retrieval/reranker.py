"""
Reranker and Resource Ranker Abstractions.
Provides deterministic multi-factor baseline scoring and optional Cross-Encoder neural reranking.
"""

from abc import ABC, abstractmethod
import asyncio
import logging
from typing import Any, Dict, List, Optional
from app.core.config import Settings, get_settings
from app.schemas.recommendation import RecommendationEvidence, RecommendationItem

logger = logging.getLogger(__name__)


class ResourceRanker(ABC):
    """Abstract interface for resource ranking models."""

    @abstractmethod
    async def rank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        learner_context: Dict[str, Any],
        verified_skills: Dict[str, float],
        skill_gaps: List[Dict[str, Any]],
        preferences: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
    ) -> List[RecommendationItem]:
        """Rank candidate resources and produce structured recommendation items."""
        pass


class DeterministicBaselineRanker(ResourceRanker):
    """
    Transparent, deterministic multi-factor ranker.
    Combines:
    1. Skill gap match weight (0.35)
    2. Semantic / retrieval similarity score (0.25)
    3. Prerequisite satisfaction (0.15)
    4. Difficulty alignment (0.10)
    5. Resource quality score (0.10)
    6. Learner format / preference match (0.05)
    """

    async def rank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        learner_context: Dict[str, Any],
        verified_skills: Dict[str, float],
        skill_gaps: List[Dict[str, Any]],
        preferences: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
    ) -> List[RecommendationItem]:
        if not candidates:
            return []

        prefs = preferences or {}
        pref_format = prefs.get("format", "").lower()
        target_difficulty = learner_context.get("experience_level", "intermediate").lower()

        # Build gap lookup map: skill_name.lower() -> gap_dict
        gap_map = {}
        for g in skill_gaps:
            if isinstance(g, dict):
                s_name = g.get("skill", "").lower()
                gap_map[s_name] = g
            elif isinstance(g, str):
                gap_map[g.lower()] = {"skill": g, "gap_magnitude": 0.5}

        verified_map = {k.lower(): v for k, v in verified_skills.items()}

        ranked_items: List[RecommendationItem] = []

        for item in candidates:
            payload = item.get("payload", item)
            res_id = str(payload.get("resource_id", item.get("id", "")))
            title = payload.get("title", f"Resource {res_id}")
            res_skills = payload.get("skills", [])
            res_prereqs = payload.get("prerequisites", [])
            res_diff = payload.get("difficulty", "intermediate").lower()
            res_type = payload.get("resource_type", "article").lower()
            quality = float(payload.get("quality_score", 0.85))
            semantic_score = float(item.get("score", item.get("rrf_score", 0.75)))
            # Normalize semantic score to 0..1
            norm_semantic = min(max(semantic_score, 0.0), 1.0)

            # Factor 1: Skill gap match
            matched_skills = []
            gap_weight = 0.0
            for s in res_skills:
                s_lower = s.lower()
                if s_lower in gap_map:
                    matched_skills.append(s)
                    gap_mag = gap_map[s_lower].get("gap_magnitude", 0.5)
                    gap_weight += gap_mag

            if res_skills:
                gap_score = min(gap_weight / len(res_skills), 1.0)
            else:
                gap_score = 0.2

            # Factor 2: Prerequisite check
            missing_prereqs = []
            for p in res_prereqs:
                p_lower = p.lower()
                if verified_map.get(p_lower, 0.0) < 0.6:
                    missing_prereqs.append(p)

            prereq_satisfied = len(missing_prereqs) == 0
            prereq_score = 1.0 if prereq_satisfied else 0.4
            prereq_status = "satisfied" if prereq_satisfied else "missing"

            # Factor 3: Difficulty alignment
            if res_diff == target_difficulty:
                diff_score = 1.0
                diff_match = "optimal"
            elif (target_difficulty == "beginner" and res_diff == "advanced") or (target_difficulty == "advanced" and res_diff == "beginner"):
                diff_score = 0.3
                diff_match = "challenging" if res_diff == "advanced" else "too_easy"
            else:
                diff_score = 0.7
                diff_match = "acceptable"

            # Factor 4: Preference match
            pref_score = 1.0 if (pref_format and pref_format in res_type) else 0.7

            # Final composite score
            final_score = (
                0.35 * gap_score
                + 0.25 * norm_semantic
                + 0.15 * prereq_score
                + 0.10 * diff_score
                + 0.10 * quality
                + 0.05 * pref_score
            )
            final_score = round(min(max(final_score, 0.0), 1.0), 4)

            # Evidence
            evidence = RecommendationEvidence(
                skill_gap_match=round(gap_score, 2),
                prerequisite_satisfied=prereq_satisfied,
                difficulty_aligned=(diff_match == "optimal"),
                matched_skills=matched_skills,
                missing_skills=missing_prereqs,
                quality_score=round(quality, 2),
            )

            primary_skill = matched_skills[0] if matched_skills else (res_skills[0] if res_skills else "General")
            reason_text = f"Curated resource for {title}. Directly addresses {primary_skill} with quality rating {quality:.2f}."

            ranked_items.append(
                RecommendationItem(
                    resource_id=res_id,
                    title=title,
                    skill_id=primary_skill,
                    score=final_score,
                    reason=reason_text,
                    source="deterministic_baseline",
                    matched_skills=matched_skills,
                    missing_skills=missing_prereqs,
                    difficulty_match=diff_match,
                    prerequisite_status=prereq_status,
                    evidence=evidence,
                )
            )

        # Sort descending by composite score
        ranked_items.sort(key=lambda x: x.score, reverse=True)
        return ranked_items[:top_k]


class CrossEncoderReranker(ResourceRanker):
    """Neural cross-encoder reranker (e.g. BAAI/bge-reranker-base)."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.model_name = settings.RERANKER_MODEL_NAME
        self.baseline = DeterministicBaselineRanker()
        self._model = None
        self._initialized = False

    def _load_model(self) -> None:
        if self._initialized:
            return
        try:
            from sentence_transformers import CrossEncoder
            if self.settings.RERANKER_DEVICE != "cuda":
                raise RuntimeError("RERANKER_DEVICE must be set to 'cuda' for production inference.")
            self._model = CrossEncoder(self.model_name, device=self.settings.RERANKER_DEVICE)
            self._initialized = True
            logger.info(f"CrossEncoder Reranker loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"Could not load CUDA CrossEncoder model: {e}", exc_info=True)
            raise RuntimeError("CUDA reranker initialization failed; refusing CPU baseline fallback.") from e

    async def rank(
        self,
        query: str,
        candidates: List[Dict[str, Any]],
        learner_context: Dict[str, Any],
        verified_skills: Dict[str, float],
        skill_gaps: List[Dict[str, Any]],
        preferences: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
    ) -> List[RecommendationItem]:
        # First compute baseline items
        baseline_items = await self.baseline.rank(
            query=query,
            candidates=candidates,
            learner_context=learner_context,
            verified_skills=verified_skills,
            skill_gaps=skill_gaps,
            preferences=preferences,
            top_k=len(candidates),
        )

        if not self.settings.ENABLE_RERANKING or not self._model:
            return baseline_items[:top_k]

        def _predict_sync():
            pairs = [[query, item.title or ""] for item in baseline_items]
            scores = self._model.predict(pairs)
            return scores

        try:
            neural_scores = await asyncio.to_thread(_predict_sync)
            for item, n_score in zip(baseline_items, neural_scores):
                # Blend baseline score (0.4) and neural cross-encoder score (0.6)
                sigmoid_n = 1.0 / (1.0 + float(2.71828 ** (-n_score)))
                item.score = round(0.4 * item.score + 0.6 * sigmoid_n, 4)
                item.source = "neural_reranker"
            baseline_items.sort(key=lambda x: x.score, reverse=True)
        except Exception as exc:
            logger.warning(f"Reranking error: {exc}. Returning baseline ranking.")

        return baseline_items[:top_k]


def get_resource_ranker(settings: Optional[Settings] = None) -> ResourceRanker:
    cfg = settings or get_settings()
    if cfg.ENABLE_RERANKING and not cfg.AI_MOCK_MODE:
        return CrossEncoderReranker(cfg)
    return DeterministicBaselineRanker()
