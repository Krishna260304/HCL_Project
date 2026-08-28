"""
Assessment Generation and Question Quality Psychometric Metrics.
"""

from typing import List, Set
from app.schemas.assessment import MCQQuestion
from app.validation.question_validator import QuestionValidator


def calculate_validity_rate(questions: List[MCQQuestion]) -> float:
    """Calculate percentage of questions that pass strict deterministic validation."""
    if not questions:
        return 0.0
    valid, _ = QuestionValidator.validate_assessment_batch(questions)
    return round(len(valid) / len(questions), 4)


def calculate_skill_coverage(questions: List[MCQQuestion], target_skills: Set[str]) -> float:
    """Calculate the ratio of target skills tested by the assessment batch."""
    if not target_skills:
        return 1.0
    tested_skills = {q.get_skill().lower() for q in questions if q.get_skill()}
    covered = sum(1 for s in target_skills if s.lower() in tested_skills)
    return round(covered / len(target_skills), 4)
