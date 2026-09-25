import json
import math
import os
from datetime import datetime

from sentence_transformers import SentenceTransformer


class LongTermMemory:

    MEMORY_TYPES = {
        "fact",
        "preference",
        "goal",
        "research",
        "strategy",
        "outcome"
    }

    def __init__(
        self,
        file_path="long_term_memory.json"
    ):

        self.file_path = file_path

        self.embedding_model_name = (
            "all-MiniLM-L6-v2"
        )

        self.embedding_model = SentenceTransformer(
            self.embedding_model_name
        )

        self.records = self._load()

        self._rebuild_embeddings()

    def _load(self):

        if not os.path.exists(
            self.file_path
        ):

            return []

        try:

            with open(
                self.file_path,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            return (
                data
                if isinstance(data, list)
                else []
            )

        except (
            json.JSONDecodeError,
            OSError
        ):

            return []

    def _save(self):

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.records,
                file,
                indent=2,
                ensure_ascii=False
            )

    def _rebuild_embeddings(self):

        texts = [
            record.get(
                "content",
                ""
            )
            for record in self.records
        ]

        if not texts:

            return

        embeddings = self.embedding_model.encode(
            texts,
            normalize_embeddings=True
        )

        for record, embedding in zip(
            self.records,
            embeddings
        ):

            record["embedding"] = (
                embedding.tolist()
            )

    def add(
        self,
        memory_type,
        content,
        importance=1
    ):

        if memory_type not in self.MEMORY_TYPES:

            raise ValueError(
                f"Invalid memory type: {memory_type}"
            )

        embedding = self.embedding_model.encode(
            content,
            normalize_embeddings=True
        )

        record = {
            "id": len(self.records) + 1,
            "timestamp": datetime.now().isoformat(),
            "type": memory_type,
            "content": content,
            "importance": max(
                1,
                min(
                    int(importance),
                    10
                )
            ),
            "embedding": embedding.tolist()
        }

        self.records.append(
            record
        )

        if len(self.records) > 1000:

            self.records = (
                self.records[-1000:]
            )

        self._save()

        return record

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

    def search(
        self,
        query,
        top_k=5,
        memory_type=None,
        similarity_threshold=0.35
    ):

        if not self.records:

            return []

        query_embedding = (
            self.embedding_model.encode(
                query,
                normalize_embeddings=True
            )
        )

        scored = []

        for record in self.records:

            if (
                memory_type
                and record.get("type")
                != memory_type
            ):

                continue

            embedding = record.get(
                "embedding"
            )

            if not embedding:

                continue

            similarity = (
                self._cosine_similarity(
                    query_embedding,
                    embedding
                )
            )

            if similarity < similarity_threshold:

                continue

            scored.append(
                {
                    "id": record["id"],
                    "type": record["type"],
                    "content": record["content"],
                    "importance": record["importance"],
                    "timestamp": record["timestamp"],
                    "similarity": round(
                        similarity,
                        4
                    )
                }
            )

        scored.sort(
            key=lambda item: (
                item["similarity"],
                item["importance"]
            ),
            reverse=True
        )

        return scored[:top_k]

    def retrieve_context(
        self,
        query,
        top_k=5
    ):

        memories = self.search(
            query=query,
            top_k=top_k
        )

        if not memories:

            return (
                "No relevant long-term memories "
                "were found."
            )

        lines = [
            "RELEVANT LONG-TERM MEMORIES:"
        ]

        for memory in memories:

            lines.append(
                f"- [{memory['type']}] "
                f"{memory['content']} "
                f"(similarity: "
                f"{memory['similarity']:.4f}, "
                f"importance: "
                f"{memory['importance']}/10)"
            )

        return "\n".join(
            lines
        )

    def recent(
        self,
        limit=10
    ):

        return self.records[-limit:]

    def get_by_type(
        self,
        memory_type,
        limit=20
    ):

        results = [
            record
            for record in self.records
            if record.get("type")
            == memory_type
        ]

        return results[-limit:]

    def context(
        self,
        limit=20
    ):

        records = self.recent(
            limit
        )

        if not records:

            return (
                "No long-term memories "
                "are available."
            )

        lines = [
            "LONG-TERM MEMORY:"
        ]

        for record in records:

            lines.append(
                f"- [{record['type']}] "
                f"{record['content']} "
                f"(importance: "
                f"{record['importance']}/10)"
            )

        return "\n".join(
            lines
        )

    def statistics(self):

        counts = {}

        for record in self.records:

            memory_type = record.get(
                "type",
                "unknown"
            )

            counts[memory_type] = (
                counts.get(
                    memory_type,
                    0
                ) + 1
            )

        return {
            "total_memories": len(
                self.records
            ),
            "by_type": counts,
            "embedding_model": (
                self.embedding_model_name
            )
        }