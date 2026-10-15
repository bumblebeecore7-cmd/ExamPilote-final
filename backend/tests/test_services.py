import pytest
from app.providers.mock_provider import MockAIProvider
from app.schemas.question import DifficultyLevel, QuestionFormat, QuestionGenerateRequest
from app.schemas.quiz import QuizAttemptSubmit
from app.services.quiz_service import QuizService

@pytest.mark.asyncio
async def test_mock_provider_generation():
    provider = MockAIProvider(model_name="test-model")
    req = QuestionGenerateRequest(
        topic="Computer Networks",
        question_count=4,
        difficulty=DifficultyLevel.HARD,
        format=QuestionFormat.SINGLE
    )
    questions = await provider.generate_questions(req)
    assert len(questions) == 4
    for q in questions:
        assert q.difficulty == DifficultyLevel.HARD
        assert q.correct_answer in q.options
        assert len(q.options) == 4
        assert len(q.explanation) > 5

@pytest.mark.asyncio
async def test_mock_provider_true_false():
    provider = MockAIProvider(model_name="test-model")
    req = QuestionGenerateRequest(
        topic="Biology",
        question_count=3,
        difficulty=DifficultyLevel.EASY,
        format=QuestionFormat.TRUE_FALSE
    )
    questions = await provider.generate_questions(req)
    assert len(questions) == 3
    for q in questions:
        assert q.format == QuestionFormat.TRUE_FALSE
        assert q.options == ["True", "False"]
        assert q.correct_answer in ["True", "False"]

def test_quiz_scoring_logic(monkeypatch):
    # Mock QuestionRepository.get_by_id
    fake_question_set = {
        "id": "507f1f77bcf86cd799439011",
        "topic": "World History",
        "questions": [
            {
                "id": "q1",
                "question": "Question 1?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Exp 1"
            },
            {
                "id": "q2",
                "question": "Question 2?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "B",
                "explanation": "Exp 2"
            }
        ]
    }

    # Mock repository methods
    from app.repositories.question_repository import QuestionRepository
    from app.repositories.quiz_attempt_repository import QuizAttemptRepository

    monkeypatch.setattr(QuestionRepository, "get_by_id", lambda q_id: fake_question_set)
    monkeypatch.setattr(QuizAttemptRepository, "create", lambda doc: {**doc, "id": "fake_attempt_123"})

    # Submission with 1 correct, 1 wrong
    submission = QuizAttemptSubmit(
        question_set_id="507f1f77bcf86cd799439011",
        answers={"q1": "A", "q2": "C"},
        time_spent_seconds=60
    )

    result = QuizService.evaluate_and_submit(submission)
    assert result["total_questions"] == 2
    assert result["correct_count"] == 1
    assert result["incorrect_count"] == 1
    assert result["unanswered_count"] == 0
    assert result["score"] == 1
    assert result["percentage"] == 50.0
    assert len(result["reviews"]) == 2
    assert result["reviews"][0]["is_correct"] is True
    assert result["reviews"][1]["is_correct"] is False
