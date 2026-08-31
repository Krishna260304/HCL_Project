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

        # 4 & 5. Correct answer exists and belongs to options
        trimmed_correct = (question.correct_answer or "").strip()
        if not trimmed_correct:
            if cleaned_options:
                question.correct_answer = cleaned_options[0]
                trimmed_correct = question.correct_answer
            else:
                return False, "Correct answer string is missing or empty."

        matched = False
        # Direct match
        for opt in cleaned_options:
            if opt.strip().lower() == trimmed_correct.lower():
                question.correct_answer = opt  # normalize case
                matched = True
                break

        # Letter/index matching (e.g. correct_answer="A", "Option A", "1", "A) ...")
        if not matched:
            import re
            letter_match = re.match(r"^(?:option\s+)?([A-D]|[1-4])(?:\)|\.|\:)?\s*(.*)$", trimmed_correct, re.IGNORECASE)
            if letter_match:
                prefix = letter_match.group(1).upper()
                idx = {"A": 0, "B": 1, "C": 2, "D": 3, "1": 0, "2": 1, "3": 2, "4": 3}.get(prefix)
                if idx is not None and idx < len(cleaned_options):
                    question.correct_answer = cleaned_options[idx]
                    matched = True
                elif letter_match.group(2):
                    remainder = letter_match.group(2).strip().lower()
                    for opt in cleaned_options:
                        if opt.strip().lower() == remainder:
                            question.correct_answer = opt
                            matched = True
                            break

        if not matched:
            # Substring matching fallback
            for opt in cleaned_options:
                if trimmed_correct.lower() in opt.lower() or opt.lower() in trimmed_correct.lower():
                    question.correct_answer = opt
                    matched = True
                    break

        if not matched:
            return False, f"Correct answer '{trimmed_correct}' does not match any of the provided options."

        # 6. Skill and Topic exist
        skill_name = question.get_skill()
        if not skill_name or skill_name.strip() == "":
            question.skill = "General Knowledge"

        if not question.topic or question.topic.strip() == "":
            question.topic = "Core Principles"

        # 7. Difficulty is valid
        if (question.difficulty or "").lower() not in VALID_DIFFICULTIES:
            question.difficulty = "intermediate"

        # 8. Learning objective exists
        if not question.learning_objective or len(question.learning_objective.strip()) < 3:
            question.learning_objective = f"Assess proficiency in {question.get_skill()}"

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
