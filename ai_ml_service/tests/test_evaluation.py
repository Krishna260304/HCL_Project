"""
Tests for Evaluation Metric Functions.
"""

from app.evaluation.assessment_metrics import calculate_skill_coverage, calculate_validity_rate
from app.evaluation.recommendation_metrics import mean_reciprocal_rank, ndcg_at_k, precision_at_k, recall_at_k
from app.evaluation.retrieval_metrics import hit_rate_at_k, retrieval_recall_at_k
from app.schemas.assessment import MCQQuestion


def test_recommendation_metrics_calculation():
    recs = ["d1", "d2", "d3", "d4", "d5"]
    ground_truth = {"d1", "d3"}

    p_at_2 = precision_at_k(recs, ground_truth, k=2)  # d1 hit out of 2 -> 0.5
    assert p_at_2 == 0.5

    r_at_3 = recall_at_k(recs, ground_truth, k=3)    # d1 and d3 hits out of 2 -> 1.0
    assert r_at_3 == 1.0

    mrr = mean_reciprocal_rank(recs, ground_truth)    # first hit at rank 1 -> 1.0
    assert mrr == 1.0

    ndcg = ndcg_at_k(recs, ground_truth, k=3)
    assert ndcg > 0.8


def test_retrieval_metrics_calculation():
    retrieved = ["a", "b", "c"]
    target = {"c", "d"}

    rec = retrieval_recall_at_k(retrieved, target, k=3)
    assert rec == 0.5

    hit = hit_rate_at_k(retrieved, target, k=3)
    assert hit == 1.0


def test_assessment_metrics():
    q_valid = MCQQuestion(
        question="What is backpropagation?",
        options=["Gradient calculation", "Static typing"],
        correct_answer="Gradient calculation",
        skill="Deep Learning",
        topic="Backpropagation",
        difficulty="intermediate",
        learning_objective="Understand backprop",
        explanation="Gradient calculation",
    )
    val_rate = calculate_validity_rate([q_valid])
    assert val_rate == 1.0

    cov_rate = calculate_skill_coverage([q_valid], {"Deep Learning", "MLOps"})
    assert cov_rate == 0.5
