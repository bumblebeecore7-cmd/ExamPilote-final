import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("exampilote")

# Locate frontend directory (one level above backend)
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Keep startup independent of external services. MongoDB Atlas can be
    # temporarily unavailable (or misconfigured) without preventing the web
    # service from starting and serving the frontend/health endpoint.
    logger.info("Starting ExamPilote Backend Application...")
    logger.info(f"Target Database: {settings.MONGODB_DATABASE}")
    logger.info(f"Active AI Provider: {settings.AI_PROVIDER}")
    logger.info("MongoDB Atlas will be checked when a database endpoint is used.")

    yield

    # Shutdown actions
    logger.info("Shutting down ExamPilote Backend Application...")
    DatabaseManager.close()

app = FastAPI(
    title="ExamPilote API",
    description="Complete AI MCQ Generation Platform with MongoDB Atlas Persistence",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS (allow all in production or configured origins)
origins = [
    settings.FRONTEND_ORIGIN,
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "production" else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global safe error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again later."}
    )

# Include API v1 routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/healthz", include_in_schema=False)
def platform_health_check():
    """Fast, dependency-free liveness probe for hosting platforms."""
    return {"status": "ok"}

@app.get("/api/status", summary="API Status")
def api_status():
    return {
        "name": "ExamPilote API",
        "status": "online",
        "documentation": "/docs",
        "version": "1.0.0"
    }

# Mount static frontend at root for single-service full-stack deployment
if FRONTEND_DIR.exists():
    logger.info(f"Mounting static frontend from {FRONTEND_DIR}")
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
else:
    @app.get("/", summary="Root Status")
    def root():
        return {
            "name": "ExamPilote API",
            "status": "online",
            "documentation": "/docs",
            "version": "1.0.0"
        }
