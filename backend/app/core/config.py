from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine base paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    # MongoDB Atlas Settings
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "exampilote"

    # Server Settings
    ENVIRONMENT: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    FRONTEND_ORIGIN: str = "http://localhost:5500"

    # AI Provider Settings
    AI_PROVIDER: str = "gemini"
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gemini-flash-lite-latest"

    # Generation Limits & Defaults
    MAX_QUESTIONS_PER_REQUEST: int = 20
    DEFAULT_QUESTION_COUNT: int = 5
    DEFAULT_DIFFICULTY: str = "Medium"
    DEFAULT_FORMAT: str = "Single-correct MCQ"

    # Upload configuration
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: str = ".txt,.pdf,.docx"

    model_config = SettingsConfigDict(
        env_file=(
            str(BACKEND_DIR / ".env"),
            str(ROOT_DIR / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(",") if ext.strip()]

settings = Settings()
