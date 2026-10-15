import logging
from datetime import datetime, timezone
from typing import Any, Dict, List
from fastapi import HTTPException, status
from app.repositories.question_repository import QuestionRepository
from app.repositories.quiz_attempt_repository import QuizAttemptRepository
from app.schemas.quiz import (
    QuizAttemptResponse,
    QuizAttemptSubmit,
    QuizQuestionReview
)

logger = logging.getLogger("exampilote.services.quiz")

class QuizService:
    """Service evaluating quiz answers, computing scoring metrics, and saving attempts."""

    @classmethod
    def evaluate_and_submit(cls, submission: QuizAttemptSubmit) -> Dict[str, Any]:
        # 1. Fetch Question Set
        q_set = QuestionRepository.get_by_id(submission.question_set_id)
        if not q_set:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question set with ID '{submission.question_set_id}' not found."
            )

        questions = q_set.get("questions", [])
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question set contains no questions to score."
            )

        total_questions = len(questions)
        correct_count = 0
        incorrect_count = 0
        unanswered_count = 0
        reviews: List[Dict[str, Any]] = []

        for q in questions:
            q_id = q.get("id")
            correct_ans = q.get("correct_answer", "").strip()
            selected = submission.answers.get(q_id)
            if selected is not None:
                selected = selected.strip()

            if not selected:
                unanswered_count += 1
                is_correct = False
            elif selected == correct_ans:
                correct_count += 1
                is_correct = True
            else:
                incorrect_count += 1
                is_correct = False

            reviews.append({
                "question_id": q_id,
                "question": q.get("question", ""),
                "options": q.get("options", []),
                "selected_answer": selected,
                "correct_answer": correct_ans,
                "is_correct": is_correct,
                "explanation": q.get("explanation", "")
            })

        score = correct_count
        percentage = round((correct_count / total_questions) * 100.0, 2) if total_questions > 0 else 0.0

        attempt_doc = {
            "question_set_id": submission.question_set_id,
            "topic": q_set.get("topic", "Quiz"),
            "total_questions": total_questions,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "unanswered_count": unanswered_count,
            "score": score,
            "percentage": percentage,
            "time_spent_seconds": submission.time_spent_seconds or 0,
            "reviews": reviews,
            "submitted_at": datetime.now(timezone.utc)
        }

        try:
            saved_attempt = QuizAttemptRepository.create(attempt_doc)
            return saved_attempt
        except Exception as e:
            logger.error(f"Failed to persist quiz attempt in database: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Scoring completed, but saving attempt to MongoDB Atlas failed: {type(e).__name__}."
            )
