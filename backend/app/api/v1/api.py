from fastapi import APIRouter
from app.api.v1.endpoints import health, questions, quiz

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(questions.router, tags=["Questions"])
api_router.include_router(quiz.router, tags=["Quiz"])
