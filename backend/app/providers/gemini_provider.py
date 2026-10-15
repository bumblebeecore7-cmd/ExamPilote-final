import json
import logging
import re
from pathlib import Path
from typing import List
import httpx
from app.providers.base import BaseAIProvider
from app.schemas.question import QuestionGenerateRequest, QuestionItem

logger = logging.getLogger("exampilote.providers.gemini")

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

# Fallback sequence in case of 503 high demand or 429 rate limit
FALLBACK_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
    "gemini-2.5-flash-lite",
    "gemini-3.1-flash-lite-preview"
]

class GeminiAIProvider(BaseAIProvider):
    """Google Gemini AI Provider utilizing the REST API with automatic multi-model fallback."""

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _load_prompts(self) -> tuple[str, str]:
        system_file = PROMPTS_DIR / "mcq_system.txt"
        gen_file = PROMPTS_DIR / "mcq_generation.txt"
        
        system_prompt = system_file.read_text(encoding="utf-8") if system_file.exists() else ""
        gen_prompt = gen_file.read_text(encoding="utf-8") if gen_file.exists() else ""
        return system_prompt, gen_prompt

    async def generate_questions(self, request: QuestionGenerateRequest) -> List[QuestionItem]:
        if not self.api_key:
            raise ValueError(
                "Gemini API key is not configured. Please set AI_API_KEY in backend/.env to use Gemini, "
                "or switch AI_PROVIDER=mock."
            )

        system_template, gen_template = self._load_prompts()

        # Build prompt sections
        material_section = ""
        if request.study_material and request.study_material.strip():
            material_section = f"Source Study Material:\n\"\"\"\n{request.study_material.strip()}\n\"\"\""

        custom_section = ""
        if request.custom_instructions and request.custom_instructions.strip():
            custom_section = f"Special Instructions:\n{request.custom_instructions.strip()}"

        user_content = gen_template.format(
            question_count=request.question_count,
            difficulty=request.difficulty.value,
            format=request.format.value,
            topic=request.topic or "Extracted Study Material",
            study_material_section=material_section,
            custom_instructions_section=custom_section
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": user_content}]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.4
            }
        }
        if system_template:
            payload["systemInstruction"] = {
                "parts": [{"text": system_template}]
            }

        # Candidate models to try in sequence
        candidate_models = [self.model_name] + [m for m in FALLBACK_MODELS if m != self.model_name]
        last_error = None

        async with httpx.AsyncClient(timeout=12.0) as client:
            for model_candidate in candidate_models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_candidate}:generateContent?key={self.api_key}"
                try:
                    logger.info(f"Querying Gemini model '{model_candidate}'...")
                    response = await client.post(url, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            raw_text = candidates[0]["content"]["parts"][0]["text"].strip()
                            # Clean markdown code blocks if present
                            cleaned_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                            cleaned_text = re.sub(r"\s*```$", "", cleaned_text).strip()

                            parsed_list = json.loads(cleaned_text)
                            if isinstance(parsed_list, list) and len(parsed_list) > 0:
                                validated_questions: List[QuestionItem] = []
                                for item in parsed_list:
                                    validated_questions.append(QuestionItem.model_validate(item))
                                
                                logger.info(f"Successfully generated {len(validated_questions)} questions with '{model_candidate}'!")
                                return validated_questions

                    logger.warning(f"Model '{model_candidate}' returned status {response.status_code}. Attempting fallback...")
                    last_error = f"Status {response.status_code}: {response.text[:200]}"

                except Exception as e:
                    logger.warning(f"Model '{model_candidate}' failed ({type(e).__name__}: {e}). Trying next fallback model...")
                    last_error = str(e)

        raise RuntimeError(f"All Gemini models exhausted. Last error: {last_error}")
