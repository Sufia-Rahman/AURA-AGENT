import json


class MemoryFormation:

    def __init__(
        self,
        client,
        model,
        memory_manager
    ):

        self.client = client
        self.model = model
        self.memory_manager = (
            memory_manager
        )

    def extract(
        self,
        user_input,
        answer
    ):

        prompt = f"""
You are AURA's memory formation module.

Your job is to identify information from an interaction
that is useful for AURA's future tasks.

User request:
{user_input}

AURA's answer:
{answer}

Only extract information that is potentially useful in
future interactions.

Possible memory types:

- fact
- preference
- goal
- research
- strategy
- outcome

Do not store temporary conversation details.
Do not invent information.
Do not store information that is not supported by the interaction.

Return exactly one JSON object:

{{
    "should_store": false,
    "memories": [
        {{
            "type": "fact",
            "content": "",
            "importance": 1
        }}
    ]
}}

Rules:

- should_store must be true only when at least one useful
  long-term memory exists.
- importance must be an integer from 1 to 10.
- Return an empty memories list when nothing should be stored.
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        text = (
            response.output_text
            .strip()
        )

        try:

            result = json.loads(
                text
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            return []

        if not result.get(
            "should_store",
            False
        ):

            return []

        memories = result.get(
            "memories",
            []
        )

        valid_memories = []

        for memory in memories:

            memory_type = (
                memory.get("type")
            )

            content = (
                memory.get(
                    "content",
                    ""
                )
                .strip()
            )

            importance = (
                memory.get(
                    "importance",
                    1
                )
            )

            if not content:
                continue

            if (
                memory_type
                not in
                self.memory_manager
                .long_term_memory
                .MEMORY_TYPES
            ):

                continue

            valid_memories.append(
                {
                    "type":
                        memory_type,

                    "content":
                        content,

                    "importance":
                        importance
                }
            )

        return (
            self.memory_manager
            .store_many(
                valid_memories
            )
        )