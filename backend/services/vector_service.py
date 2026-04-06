from infrastructure.embedding_provider import embedding_provider
from infrastructure.supabase_adapter import supabase_adapter
import logging

logger = logging.getLogger(__name__)

class VectorService:
    @staticmethod
    def embed_and_store_chunks(document_id: str, workspace_id: str, chunks: list[str]):
        """Generates embeddings for a list of text chunks and stores them in pgvector."""
        if not chunks:
            return
            
        try:
            embeddings_vectors = embedding_provider.generate_embeddings(chunks)
            
            embeddings_data = []
            for i, chunk in enumerate(chunks):
                embeddings_data.append({
                    "content": chunk,
                    "embedding": embeddings_vectors[i]
                })
                
            supabase_adapter.store_embeddings(document_id, workspace_id, embeddings_data)
        except Exception as e:
            logger.error(f"Failed to embed and store chunks: {e}")
            raise e

    @staticmethod
    def retrieve_similar_chunks(workspace_id: str, query: str, limit: int = 5) -> list[str]:
        """Gets vector representations for the query and searches pgvector."""
        try:
            query_embedding = embedding_provider.generate_query_embedding(query)
            matches = supabase_adapter.query_embeddings(workspace_id, query_embedding, limit)
            
            if not matches:
                return []
                
            return [match["content"] for match in matches]
        except Exception as e:
            logger.error(f"Failed to retrieve similar chunks: {e}")
            return []
