from sentence_transformers import CrossEncoder

class RankingService:
    def __init__(self):
        self.model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    def rank(self, query: str, chunks: list[str], top_k: int = 3) -> list[str]:
        if not chunks:
            return []

        pairs = [[query, chunk] for chunk in chunks]
        scores = self.model.predict(pairs)

        ranked = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in ranked[:top_k]]


ranking_service = RankingService()