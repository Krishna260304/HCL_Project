"""
Deterministic Multiple-Choice Question (MCQ) Validator.
Enforces rigorous psychometric and structural validity rules.
"""

from typing import Any, Dict, List, Optional, Set, Tuple
from app.schemas.assessment import MCQQuestion

VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced", "expert"}


class QuestionValidator:
    """Deterministic validation rules for assessment questions."""

    @classmethod
    def validate_single_question(cls, question: MCQQuestion) -> Tuple[bool, Optional[str]]:
        """
        Validate a single MCQ question against all deterministic rules.
        Returns (is_valid, error_message).
        """
        # 1. Question stem exists and has reasonable length
        if not question.question or len(question.question.strip()) < 8:
            return False, "Question stem is missing or too short (min 8 chars required)."

        # 2. Options exist and at least 2 options
        if not question.options or len(question.options) < 2:
            return False, "Question must have at least 2 multiple choice options."

        # 3. No duplicate options
        cleaned_options = [opt.strip() for opt in question.options]
        if len(set(cleaned_options)) != len(cleaned_options):
            return False, "Question contains duplicate options."

        # 4. Correct answer exists
        if not question.correct_answer or not question.correct_answer.strip():
            return False, "Correct answer string is missing or empty."

        # 5. Correct answer belongs to options (exact match or trimmed match)
        trimmed_correct = question.correct_answer.strip()
        matched = False
        for opt in cleaned_options:
            if opt == trimmed_correct:
                matched = True
                break
        if not matched:
            return False, f"Correct answer '{trimmed_correct}' does not match any of the provided options."

        # 6. Skill and Topic exist
        skill_name = question.get_skill()
        if not skill_name or skill_name.strip() == "":
            return False, "Question skill/skill_id is missing."

        if not question.topic or question.topic.strip() == "":
            return False, "Question topic is missing."

        # 7. Difficulty is valid
        if question.difficulty.lower() not in VALID_DIFFICULTIES:
            return False, f"Invalid difficulty '{question.difficulty}'. Allowed: {VALID_DIFFICULTIES}"

        # 8. Learning objective exists
        if not question.learning_objective or len(question.learning_objective.strip()) < 5:
            return False, "Question learning objective is missing or too short."

        return True, None

    @classmethod
    def validate_assessment_batch(
        cls, questions: List[MCQQuestion]
    ) -> Tuple[List[MCQQuestion], List[Tuple[int, MCQQuestion, str]]]:
        """
        Validate a collection of questions.
        Returns:
            valid_questions: List of questions that passed validation and deduplication
            invalid_questions: List of (index, question, failure_reason)
        """
        valid: List[MCQQuestion] = []
        invalid: List[Tuple[int, MCQQuestion, str]] = []
        seen_question_stems: Set[str] = set()

        for idx, q in enumerate(questions):
            is_valid, err = cls.validate_single_question(q)
            if not is_valid:
                invalid.append((idx, q, err or "Validation failed"))
                continue

            stem_normalized = q.question.strip().lower()
            if stem_normalized in seen_question_stems:
                invalid.append((idx, q, "Duplicate question stem in assessment batch"))
                continue

            seen_question_stems.add(stem_normalized)
            valid.append(q)

        return valid, invalid
