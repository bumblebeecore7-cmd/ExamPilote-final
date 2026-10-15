from abc import ABC, abstractmethod
from typing import Any, Dict, List
from app.schemas.question import QuestionGenerateRequest, QuestionItem

class BaseAIProvider(ABC):
    """Abstract base class for AI question generation providers."""

    def __init__(self, model_name: str, api_key: str = ""):
        self.model_name = model_name
        self.api_key = api_key

    @abstractmethod
    async def generate_questions(self, request: QuestionGenerateRequest) -> List[QuestionItem]:
        """Generates a list of validated QuestionItem instances."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'mock', 'gemini', 'openai')."""
        pass
