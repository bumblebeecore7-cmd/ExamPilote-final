from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class QuestionFormat(str, Enum):
    SINGLE = "Single-correct MCQ"
    TRUE_FALSE = "True/False"
    MIXED = "Mixed"

class QuestionItem(BaseModel):
    id: str = Field(..., description="Unique question identifier")
    question: str = Field(..., min_length=5, description="Clear question text")
    options: List[str] = Field(..., description="List of possible answer choices")
    correct_answer: str = Field(..., description="The correct answer string, must match one of the options")
    explanation: str = Field(..., min_length=5, description="Educational explanation for why the answer is correct")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    format: QuestionFormat = Field(default=QuestionFormat.SINGLE)
    source_reference: Optional[str] = Field(default=None, description="Source context reference if available")

    @field_validator("options")
    @classmethod
    def validate_options_length(cls, v: List[str]) -> List[str]:
        cleaned = [opt.strip() for opt in v if opt.strip()]
        if len(cleaned) < 2:
            raise ValueError("A question must have at least 2 non-empty options")
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("All options for a question must be distinct")
        return cleaned

    @model_validator(mode="after")
    def validate_correct_answer_in_options(self) -> "QuestionItem":
        cleaned_options = [opt.strip() for opt in self.options]
        cleaned_correct = self.correct_answer.strip()
        if cleaned_correct not in cleaned_options:
            raise ValueError(
                f"Correct answer '{cleaned_correct}' does not match any of the available options: {cleaned_options}"
            )
        # Format-specific check
        if self.format == QuestionFormat.TRUE_FALSE and len(cleaned_options) != 2:
            raise ValueError("True/False questions must have exactly 2 options")
        if self.format == QuestionFormat.SINGLE and len(cleaned_options) != 4:
            # We enforce standard 4-option MCQs for Single-correct MCQ
            if len(cleaned_options) < 3 or len(cleaned_options) > 5:
                raise ValueError("Standard MCQ must contain between 3 and 5 options (typically 4)")
        return self

class QuestionGenerateRequest(BaseModel):
    topic: Optional[str] = Field(default="", description="Subject or topic for generation")
    study_material: Optional[str] = Field(default="", description="Pasted notes or study material text")
    question_count: int = Field(default=5, ge=1, le=20, description="Number of questions to generate (1-20)")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM)
    format: QuestionFormat = Field(default=QuestionFormat.SINGLE)
    custom_instructions: Optional[str] = Field(default="", description="Optional additional instructions")

    @model_validator(mode="after")
    def validate_input_present(self) -> "QuestionGenerateRequest":
        t = (self.topic or "").strip()
        s = (self.study_material or "").strip()
        if not t and not s:
            raise ValueError("At least a topic or study material must be provided for MCQ generation.")
        return self

class QuestionSetResponse(BaseModel):
    id: str
    topic: str
    questions: List[QuestionItem]
    difficulty: str
    format: str
    question_count: int
    provider: str
    model: str
    saved_to_atlas: bool = True
    storage_warning: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QuestionSetListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[QuestionSetResponse]
