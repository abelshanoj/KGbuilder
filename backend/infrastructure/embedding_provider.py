import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    def __init__(self):
        try:
            self.model_name = "all-MiniLM-L6-v2"
            self.model = SentenceTransformer(self.model_name)

            logger.info(f"SentenceTransformer '{self.model_name}' loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.model = None

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not self.model:
            raise ValueError("Embedding model not initialized")

        try:
            embeddings = self.model.encode(
                texts,
                batch_size=32,
                show_progress_bar=False,
                normalize_embeddings=True  # IMPORTANT for cosine similarity
            )

            return embeddings.tolist()

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise

    def generate_query_embedding(self, query: str) -> list[float]:
        if not self.model:
            raise ValueError("Embedding model not initialized")

        try:
            embedding = self.model.encode(
                query,
                normalize_embeddings=True
            )

            return embedding.tolist()

        except Exception as e:
            logger.error(f"Query embedding failed: {e}")
            raise


embedding_provider = EmbeddingProvider()