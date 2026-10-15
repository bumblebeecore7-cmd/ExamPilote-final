from app.core.config import settings
from app.providers.base import BaseAIProvider
from app.providers.mock_provider import MockAIProvider
from app.providers.gemini_provider import GeminiAIProvider

def get_ai_provider() -> BaseAIProvider:
    """Factory function that returns the configured AI provider implementation."""
    provider_type = settings.AI_PROVIDER.lower().strip()
    if provider_type == "gemini":
        return GeminiAIProvider(
            model_name=settings.AI_MODEL,
            api_key=settings.AI_API_KEY or ""
        )
    # Default to Mock provider for local, offline, or zero-cost execution
    return MockAIProvider(model_name="mock-model")
