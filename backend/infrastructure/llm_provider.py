from groq import Groq
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class LLMProvider:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY is missing")
            self.client = None
            return
            
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def generate_json(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model: str = "llama-3.1-8b-instant") -> str:
        if not self.client:
            raise ValueError("Groq client not initialized")
            
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model=model,
            response_format={ "type": "json_object" }
        )
        return response.choices[0].message.content

    def generate_text(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model: str = "llama-3.1-8b-instant") -> str:
        if not self.client:
            raise ValueError("Groq client not initialized")
            
        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model=model
        )
        return response.choices[0].message.content

llm_provider = LLMProvider()
