"""
Evaluation script to execute offline metrics benchmarking across recommendation, retrieval, and psychometrics.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.evaluation.assessment_metrics import calculate_skill_coverage, calculate_validity_rate
from app.evaluation.recommendation_metrics import mean_reciprocal_rank, ndcg_at_k, precision_at_k, recall_at_k
from app.evaluation.retrieval_metrics import hit_rate_at_k, retrieval_recall_at_k
from app.schemas.assessment import MCQQuestion


def run_evaluation_suite():
    print("============================================================")
    print(" Running LearnPath AI/ML Offline Evaluation Suite")
    print("============================================================")

    # 1. Recommendation Ranking Evaluation
    recommended = ["res_ml_01", "res_dl_01", "res_py_01", "res_mlops_01", "res_other"]
    ground_truth = {"res_ml_01", "res_dl_01"}

    p_at_3 = precision_at_k(recommended, ground_truth, k=3)
    r_at_3 = recall_at_k(recommended, ground_truth, k=3)
    ndcg_3 = ndcg_at_k(recommended, ground_truth, k=3)
    mrr = mean_reciprocal_rank(recommended, ground_truth)

    print(f"Recommendation Precision@3: {p_at_3:.4f}")
    print(f"Recommendation Recall@3:    {r_at_3:.4f}")
    print(f"Recommendation NDCG@3:      {ndcg_3:.4f}")
    print(f"Recommendation MRR:         {mrr:.4f}")

    # 2. Retrieval Evaluation
    retrieved = ["res_ml_01", "res_misc", "res_dl_01"]
    ret_recall = retrieval_recall_at_k(retrieved, ground_truth, k=3)
    hit_rate = hit_rate_at_k(retrieved, ground_truth, k=3)
    print(f"Retrieval Recall@3:         {ret_recall:.4f}")
    print(f"Retrieval HitRate@3:        {hit_rate:.4f}")

    # 3. Assessment Evaluation
    sample_questions = [
        MCQQuestion(
            id="q1",
            question="What is the purpose of backpropagation in deep neural networks?",
            options=[
                "Compute gradients of loss function with respect to weights using chain rule",
                "Perform static compilation of Python scripts",
                "Allocate random tensors in system memory",
                "Encrypt model parameters on disk",
            ],
            correct_answer="Compute gradients of loss function with respect to weights using chain rule",
            skill="Deep Learning",
            topic="Backpropagation",
            difficulty="intermediate",
            learning_objective="Understand chain rule gradient calculation",
            explanation="Backpropagation recursively applies the calculus chain rule backwards from the loss output.",
        )
    ]
    val_rate = calculate_validity_rate(sample_questions)
    cov_rate = calculate_skill_coverage(sample_questions, {"Deep Learning", "Python"})
    print(f"Assessment Validity Rate:   {val_rate * 100:.1f}%")
    print(f"Assessment Skill Coverage:  {cov_rate * 100:.1f}%")
    print("============================================================")


if __name__ == "__main__":
    run_evaluation_suite()
