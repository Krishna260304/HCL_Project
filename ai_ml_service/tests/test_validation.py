"""
Tests for Deterministic Validation Rules.
"""

from app.schemas.assessment import MCQQuestion
from app.schemas.learning_path import LearningPathData, LearningPhase
from app.schemas.resource import ResourcePayload
from app.validation.learning_path_validator import LearningPathValidator
from app.validation.question_validator import QuestionValidator
from app.validation.resource_validator import ResourceValidator


def test_question_validator_rejects_missing_correct_answer():
    q = MCQQuestion(
        question="What is gradient descent?",
        options=["Optimization algorithm", "Loss function", "Dataset"],
        correct_answer="Non existent option",  # Invalid
        skill="Machine Learning",
        topic="Optimization",
        difficulty="intermediate",
        learning_objective="Understand gradient descent",
        explanation="Optimization algorithm",
    )
    is_valid, err = QuestionValidator.validate_single_question(q)
    assert is_valid is False
    assert "does not match any of the provided options" in err


def test_question_validator_rejects_duplicate_options():
    q = MCQQuestion(
        question="What is gradient descent?",
        options=["Optimization algorithm", "Optimization algorithm"],  # Duplicate
        correct_answer="Optimization algorithm",
        skill="Machine Learning",
        topic="Optimization",
        difficulty="intermediate",
        learning_objective="Understand gradient descent",
        explanation="Optimization algorithm",
    )
    is_valid, err = QuestionValidator.validate_single_question(q)
    assert is_valid is False
    assert "duplicate options" in err.lower()


def test_learning_path_validator_detects_cycles():
    # Phase 1 requires Phase 2 skill, Phase 2 requires Phase 1 skill -> Circular dependency
    phases = [
        LearningPhase(
            phase_id="p1",
            title="Phase 1",
            description="Phase 1 desc",
            order=1,
            skills=["SkillA"],
            prerequisites=["SkillB"],
        ),
        LearningPhase(
            phase_id="p2",
            title="Phase 2",
            description="Phase 2 desc",
            order=2,
            skills=["SkillB"],
            prerequisites=["SkillA"],
        ),
    ]
    path = LearningPathData(
        title="Cyclic Roadmap",
        description="Path with circular dependency",
        goal="AI Engineer",
        phases=phases,
    )
    is_valid, errors = LearningPathValidator.validate_path(path)
    assert is_valid is False
    assert any("Circular dependency" in e for e in errors)


def test_resource_validator():
    # Construct with model_construct to bypass initial pydantic raise and test validator directly
    res_invalid = ResourcePayload.model_construct(
        resource_id="",
        source="test",
        title="Ab",
        duration_minutes=0,
        quality_score=1.5,
    )
    is_valid, err = ResourceValidator.validate(res_invalid)
    assert is_valid is False
    assert err is not None

    res_valid = ResourcePayload(
        resource_id="res_101",
        source="youtube",
        title="Valid Resource Title",
        duration_minutes=45,
        quality_score=0.9,
    )
    is_valid, err = ResourceValidator.validate(res_valid)
    assert is_valid is True
