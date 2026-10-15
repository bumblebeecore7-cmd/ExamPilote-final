from fastapi import APIRouter
from app.core.config import settings
from app.core.database import DatabaseManager

router = APIRouter()

@router.get("/health", summary="Basic API Health Check")
def health_check():
    """Returns general service health status."""
    return {
        "status": "healthy",
        "service": "ExamPilote API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "ai_provider": settings.AI_PROVIDER
    }

@router.get("/health/database", summary="MongoDB Atlas Health Check")
def database_health_check():
    """Verifies live connectivity to MongoDB Atlas with a database ping command."""
    ping_result = DatabaseManager.ping()
    masked_uri = DatabaseManager.get_masked_uri()
    return {
        "status": "connected" if ping_result.get("connected") else "disconnected",
        "masked_uri": masked_uri,
        "details": ping_result
    }
