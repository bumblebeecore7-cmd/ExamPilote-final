import logging
from typing import Any, Dict
from fastapi import HTTPException, status
from app.core.config import settings
from app.providers.factory import get_ai_provider
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import QuestionGenerateRequest, QuestionSetResponse

logger = logging.getLogger("exampilote.services.generation")

class GenerationService:
    """Service orchestrating AI MCQ generation, validation, and cloud database persistence."""

    @classmethod
    async def generate_and_save(cls, request: QuestionGenerateRequest) -> Dict[str, Any]:
        provider = get_ai_provider()
        logger.info(f"Generating {request.question_count} questions via '{provider.provider_name}'...")

        try:
            questions = await provider.generate_questions(request)
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Question generation failed: {str(e)}"
            )

        if not questions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Provider returned no questions."
            )

        # Prepare document for persistence
        doc_data = {
            "topic": request.topic or "Study Material Summary",
            "study_material_snippet": (request.study_material[:300] + "...") if request.study_material else None,
            "questions": [q.model_dump() for q in questions],
            "difficulty": request.difficulty.value,
            "format": request.format.value,
            "question_count": len(questions),
            "provider": provider.provider_name,
            "model": getattr(provider, "model_name", "standard"),
            "custom_instructions": request.custom_instructions or None
        }

        # Save to repository (attempts Atlas, falls back to session if credentials pending)
        saved_doc = QuestionRepository.create(doc_data)
        return saved_doc
