class MemoryManager:

    def __init__(
        self,
        long_term_memory,
        similarity_threshold=0.85
    ):

        self.long_term_memory = (
            long_term_memory
        )

        self.similarity_threshold = (
            similarity_threshold
        )

    def _is_duplicate(
        self,
        content,
        memory_type
    ):

        matches = (
            self.long_term_memory
            .search(
                query=content,
                top_k=1,
                memory_type=memory_type,
                similarity_threshold=
                    self.similarity_threshold
            )
        )

        return matches

    def store(
        self,
        memory_type,
        content,
        importance=1
    ):

        content = content.strip()

        if not content:

            return {
                "status": "ignored",
                "reason": "Empty memory."
            }

        if (
            memory_type
            not in
            self.long_term_memory
            .MEMORY_TYPES
        ):

            return {
                "status": "ignored",
                "reason":
                    "Invalid memory type."
            }

        importance = max(
            1,
            min(
                int(importance),
                10
            )
        )

        duplicates = (
            self._is_duplicate(
                content=content,
                memory_type=memory_type
            )
        )

        if duplicates:

            existing = duplicates[0]

            if (
                importance
                > existing["importance"]
            ):

                existing_id = (
                    existing["id"]
                )

                for record in (
                    self.long_term_memory
                    .records
                ):

                    if (
                        record["id"]
                        == existing_id
                    ):

                        record[
                            "importance"
                        ] = max(
                            record[
                                "importance"
                            ],
                            importance
                        )

                        self.long_term_memory._save()

                        return {
                            "status":
                                "updated",
                            "id":
                                existing_id
                        }

            return {
                "status":
                    "duplicate",
                "id":
                    existing["id"]
            }

        record = (
            self.long_term_memory
            .add(
                memory_type=
                    memory_type,
                content=
                    content,
                importance=
                    importance
            )
        )

        return {
            "status": "stored",
            "id": record["id"]
        }

    def store_many(
        self,
        memories
    ):

        results = []

        for memory in memories:

            result = self.store(
                memory_type=
                    memory.get("type"),
                content=
                    memory.get(
                        "content",
                        ""
                    ),
                importance=
                    memory.get(
                        "importance",
                        1
                    )
            )

            results.append(
                result
            )

        return results

    def statistics(self):

        return {
            "total_memories":
                len(
                    self.long_term_memory
                    .records
                ),

            "duplicate_threshold":
                self.similarity_threshold
        }