from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class QuizAttemptSubmit(BaseModel):
    question_set_id: str = Field(..., description="ID of the question set being attempted")
    answers: Dict[str, str] = Field(default_factory=dict, description="Map of question ID to chosen option string")
    time_spent_seconds: Optional[int] = Field(default=0, ge=0, description="Time spent in seconds")

class QuizQuestionReview(BaseModel):
    question_id: str
    question: str
    options: List[str]
    selected_answer: Optional[str]
    correct_answer: str
    is_correct: bool
    explanation: str

class QuizAttemptResponse(BaseModel):
    id: str
    question_set_id: str
    topic: str
    total_questions: int
    correct_count: int
    incorrect_count: int
    unanswered_count: int
    score: int
    percentage: float
    time_spent_seconds: int
    reviews: List[QuizQuestionReview]
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QuizAttemptSummary(BaseModel):
    id: str
    question_set_id: str
    topic: str
    total_questions: int
    correct_count: int
    score: int
    percentage: float
    time_spent_seconds: int
    submitted_at: datetime

class QuizAttemptListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[QuizAttemptSummary]
