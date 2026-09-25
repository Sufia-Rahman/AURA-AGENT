import math

from sentence_transformers import SentenceTransformer


class StrategyEngine:

    def __init__(
        self,
        reflection_memory,
        similarity_threshold=0.45
    ):

        self.reflection_memory = reflection_memory

        self.similarity_threshold = (
            similarity_threshold
        )

        self.embedding_model_name = (
            "all-MiniLM-L6-v2"
        )

        self.embedding_model = SentenceTransformer(
            self.embedding_model_name
        )

    @staticmethod
    def _cosine_similarity(
        vector_a,
        vector_b
    ):

        dot_product = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b
            )
        )

        magnitude_a = math.sqrt(
            sum(
                a * a
                for a in vector_a
            )
        )

        magnitude_b = math.sqrt(
            sum(
                b * b
                for b in vector_b
            )
        )

        if (
            magnitude_a == 0
            or magnitude_b == 0
        ):

            return 0.0

        return dot_product / (
            magnitude_a *
            magnitude_b
        )

    def get_relevant_strategies(
        self,
        user_input,
        limit=10,
        top_k=3
    ):

        strategies = (
            self.reflection_memory.get_strategies(
                limit=limit
            )
        )

        if not strategies:

            return []

        task_embedding = (
            self.embedding_model.encode(
                user_input,
                normalize_embeddings=True
            )
        )

        scored_strategies = []

        for strategy in strategies:

            strategy_embedding = (
                self.embedding_model.encode(
                    strategy,
                    normalize_embeddings=True
                )
            )

            similarity = (
                self._cosine_similarity(
                    task_embedding,
                    strategy_embedding
                )
            )

            if similarity < self.similarity_threshold:

                continue

            confidence = round(
                similarity * 100,
                2
            )

            scored_strategies.append(
                {
                    "strategy": strategy,
                    "similarity": round(
                        similarity,
                        4
                    ),
                    "confidence": confidence
                }
            )

        scored_strategies.sort(
            key=lambda item: item["similarity"],
            reverse=True
        )

        return scored_strategies[:top_k]

    def build_context(
        self,
        user_input
    ):

        strategies = (
            self.get_relevant_strategies(
                user_input=user_input
            )
        )

        if not strategies:

            return (
                "No sufficiently relevant improvement "
                "strategies were found."
            )

        lines = [
            "RELEVANT IMPROVEMENT STRATEGIES:"
        ]

        for index, item in enumerate(
            strategies,
            start=1
        ):

            lines.append(
                f"{index}. {item['strategy']}"
            )

            lines.append(
                f"   Relevance: "
                f"{item['similarity']:.4f}"
            )

            lines.append(
                f"   Confidence: "
                f"{item['confidence']:.2f}%"
            )

        return "\n".join(lines)

    def statistics(
        self,
        user_input
    ):

        strategies = (
            self.get_relevant_strategies(
                user_input=user_input
            )
        )

        return {
            "strategies_found": len(strategies),
            "threshold": self.similarity_threshold,
            "embedding_model": (
                self.embedding_model_name
            ),
            "strategies": strategies
        }