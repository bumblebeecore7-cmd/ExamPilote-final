import pytest
from pydantic import ValidationError
from app.schemas.question import (
    DifficultyLevel,
    QuestionFormat,
    QuestionGenerateRequest,
    QuestionItem
)
from app.schemas.quiz import QuizAttemptSubmit

def test_question_item_valid():
    q = QuestionItem(
        id="q1",
        question="What is the capital of France?",
        options=["Paris", "London", "Berlin", "Madrid"],
        correct_answer="Paris",
        explanation="Paris is the capital and most populous city of France.",
        difficulty=DifficultyLevel.EASY,
        format=QuestionFormat.SINGLE
    )
    assert q.id == "q1"
    assert q.correct_answer == "Paris"
    assert len(q.options) == 4

def test_question_item_invalid_correct_answer():
    with pytest.raises(ValidationError):
        QuestionItem(
            id="q2",
            question="What is 2 + 2?",
            options=["1", "2", "3", "5"],
            correct_answer="4",  # Not in options
            explanation="2 + 2 is 4",
            difficulty=DifficultyLevel.EASY,
            format=QuestionFormat.SINGLE
        )

def test_true_false_format_validation():
    # Valid True/False
    q = QuestionItem(
        id="q3",
        question="The Earth is flat.",
        options=["True", "False"],
        correct_answer="False",
        explanation="The Earth is an oblate spheroid.",
        difficulty=DifficultyLevel.EASY,
        format=QuestionFormat.TRUE_FALSE
    )
    assert q.correct_answer == "False"

    # Invalid True/False with 3 options
    with pytest.raises(ValidationError):
        QuestionItem(
            id="q4",
            question="The Earth is flat.",
            options=["True", "False", "Maybe"],
            correct_answer="False",
            explanation="Explanation",
            difficulty=DifficultyLevel.EASY,
            format=QuestionFormat.TRUE_FALSE
        )

def test_question_generate_request_validation():
    # Valid with topic
    req = QuestionGenerateRequest(topic="Quantum Mechanics", question_count=5)
    assert req.topic == "Quantum Mechanics"
    assert req.question_count == 5

    # Invalid with both topic and study_material empty
    with pytest.raises(ValidationError):
        QuestionGenerateRequest(topic="", study_material="")

def test_quiz_attempt_submit():
    sub = QuizAttemptSubmit(
        question_set_id="507f1f77bcf86cd799439011",
        answers={"q1": "Paris", "q2": "False"},
        time_spent_seconds=45
    )
    assert sub.time_spent_seconds == 45
    assert len(sub.answers) == 2
