import logging
from core.config import settings
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class EmbeddingProvider:
    def __init__(self):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None)
        
        if not self.api_key:
            logger.error("❌ GEMINI_API_KEY is missing!")
            self.client = None
            return

        try:
            self.client = genai.Client(api_key=self.api_key)
            self.model_name = "gemini-embedding-001" 
            logger.info("✅ Gemini Embedding client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not self.client:
            raise ValueError("Gemini client not initialized. Check GEMINI_API_KEY")

        try:
            embeddings = []
            for text in texts:
                response = self.client.models.embed_content(
                    model=self.model_name,
                    contents=text,                    # ← Changed: pass string directly, not list
                    config=types.EmbedContentConfig(
                        task_type="SEMANTIC_SIMILARITY",
                        output_dimensionality=768
                    )
                )
                embeddings.append(response.embeddings[0].values)
            
            return embeddings
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    def generate_query_embedding(self, query: str) -> list[float]:
        if not self.client:
            raise ValueError("Gemini client not initialized")

        try:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=query,                       # ← Changed here too
                config={"task_type": "RETRIEVAL_QUERY"}
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Query embedding failed: {e}")
            raise


embedding_provider = EmbeddingProvider()