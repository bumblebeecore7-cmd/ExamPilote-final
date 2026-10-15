import pytest
import mongomock
from app.repositories.question_repository import QuestionRepository
from app.repositories.quiz_attempt_repository import QuizAttemptRepository

@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["exampilote"]
    monkeypatch.setattr(QuestionRepository, "_collection", lambda: mock_db.question_sets)
    monkeypatch.setattr(QuizAttemptRepository, "_collection", lambda: mock_db.quiz_attempts)

def test_question_set_crud():
    sample_data = {
        "topic": "Organic Chemistry",
        "questions": [
            {
                "id": "q1",
                "question": "Which functional group is present in ethanol?",
                "options": ["Hydroxyl", "Carboxyl", "Carbonyl", "Amino"],
                "correct_answer": "Hydroxyl",
                "explanation": "Ethanol is an alcohol with an -OH hydroxyl group.",
                "difficulty": "Easy",
                "format": "Single-correct MCQ"
            }
        ],
        "difficulty": "Easy",
        "format": "Single-correct MCQ",
        "question_count": 1,
        "provider": "mock",
        "model": "standard"
    }

    # 1. Create
    created = QuestionRepository.create(sample_data)
    assert "id" in created
    assert created["topic"] == "Organic Chemistry"
    assert created["schema_version"] == 1
    doc_id = created["id"]

    # 2. Get by ID
    fetched = QuestionRepository.get_by_id(doc_id)
    assert fetched is not None
    assert fetched["id"] == doc_id
    assert fetched["topic"] == "Organic Chemistry"

    # 3. List
    listed = QuestionRepository.list_all(page=1, page_size=10)
    assert listed["total"] == 1
    assert len(listed["items"]) == 1

    # 4. Delete
    deleted = QuestionRepository.delete(doc_id)
    assert deleted is True
    assert QuestionRepository.get_by_id(doc_id) is None

def test_quiz_attempt_crud():
    attempt_data = {
        "question_set_id": "507f1f77bcf86cd799439011",
        "topic": "Physics",
        "total_questions": 5,
        "correct_count": 4,
        "incorrect_count": 1,
        "unanswered_count": 0,
        "score": 4,
        "percentage": 80.0,
        "time_spent_seconds": 120,
        "reviews": []
    }

    created = QuizAttemptRepository.create(attempt_data)
    assert "id" in created
    attempt_id = created["id"]

    fetched = QuizAttemptRepository.get_by_id(attempt_id)
    assert fetched is not None
    assert fetched["score"] == 4
    assert fetched["percentage"] == 80.0

    listed = QuizAttemptRepository.list_all(page=1, page_size=10)
    assert listed["total"] == 1
    assert listed["items"][0]["score"] == 4

    by_qset = QuizAttemptRepository.get_by_question_set_id("507f1f77bcf86cd799439011")
    assert len(by_qset) == 1
