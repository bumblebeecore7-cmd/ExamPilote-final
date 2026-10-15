from fastapi import APIRouter, HTTPException, Query, status
from app.repositories.quiz_attempt_repository import QuizAttemptRepository
from app.schemas.quiz import (
    QuizAttemptListResponse,
    QuizAttemptResponse,
    QuizAttemptSubmit
)
from app.services.quiz_service import QuizService

router = APIRouter()

@router.post(
    "/quiz-attempts",
    response_model=QuizAttemptResponse,
    summary="Submit quiz attempt and get scores"
)
def submit_quiz_attempt(submission: QuizAttemptSubmit):
    """Scores a completed quiz, saves attempt to MongoDB Atlas, and returns full question reviews."""
    return QuizService.evaluate_and_submit(submission)

@router.get(
    "/quiz-attempts",
    response_model=QuizAttemptListResponse,
    summary="List previous quiz attempts"
)
def list_quiz_attempts(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50)
):
    """Retrieves paginated quiz attempts from MongoDB Atlas."""
    return QuizAttemptRepository.list_all(page=page, page_size=page_size)

@router.get(
    "/quiz-attempts/{attempt_id}",
    response_model=QuizAttemptResponse,
    summary="Get single quiz attempt details and reviews"
)
def get_quiz_attempt(attempt_id: str):
    """Retrieves full attempt details including question reviews by ID."""
    doc = QuizAttemptRepository.get_by_id(attempt_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz attempt '{attempt_id}' not found."
        )
    return doc
