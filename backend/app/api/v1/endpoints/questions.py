from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile, status
from app.repositories.question_repository import QuestionRepository
from app.schemas.question import (
    DifficultyLevel,
    QuestionFormat,
    QuestionGenerateRequest,
    QuestionSetListResponse,
    QuestionSetResponse
)
from app.services.document_service import DocumentService
from app.services.generation_service import GenerationService

router = APIRouter()

@router.post(
    "/questions/generate",
    response_model=QuestionSetResponse,
    summary="Generate questions from topic or study text"
)
async def generate_questions(request: QuestionGenerateRequest):
    """Generates MCQs from provided topic or pasted notes, validates, and persists to MongoDB Atlas."""
    saved_doc = await GenerationService.generate_and_save(request)
    return saved_doc

@router.post(
    "/questions/generate-with-document",
    response_model=QuestionSetResponse,
    summary="Generate questions with document upload"
)
async def generate_with_document(
    file: UploadFile = File(...),
    topic: Optional[str] = Form(default=""),
    question_count: int = Form(default=5),
    difficulty: DifficultyLevel = Form(default=DifficultyLevel.MEDIUM),
    format: QuestionFormat = Form(default=QuestionFormat.SINGLE),
    custom_instructions: Optional[str] = Form(default="")
):
    """Uploads a TXT, PDF, or DOCX document, extracts content, and generates questions."""
    content_bytes = await file.read()
    extracted_text = DocumentService.extract_text(file, content_bytes)

    derived_topic = topic.strip() if topic and topic.strip() else f"Document: {file.filename}"

    request = QuestionGenerateRequest(
        topic=derived_topic,
        study_material=extracted_text,
        question_count=question_count,
        difficulty=difficulty,
        format=format,
        custom_instructions=custom_instructions
    )
    saved_doc = await GenerationService.generate_and_save(request)
    return saved_doc

@router.get(
    "/question-sets",
    response_model=QuestionSetListResponse,
    summary="List saved question sets"
)
def list_question_sets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50)
):
    """Retrieves paginated question sets from MongoDB Atlas."""
    return QuestionRepository.list_all(page=page, page_size=page_size)

@router.get(
    "/question-sets/{question_set_id}",
    response_model=QuestionSetResponse,
    summary="Get single question set by ID"
)
def get_question_set(question_set_id: str):
    """Retrieves a specific question set by its ID."""
    doc = QuestionRepository.get_by_id(question_set_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question set '{question_set_id}' not found."
        )
    return doc

@router.delete(
    "/question-sets/{question_set_id}",
    summary="Delete question set by ID"
)
def delete_question_set(question_set_id: str):
    """Deletes a question set from MongoDB Atlas."""
    success = QuestionRepository.delete(question_set_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question set '{question_set_id}' not found or could not be deleted."
        )
    return {"message": "Question set deleted successfully."}
