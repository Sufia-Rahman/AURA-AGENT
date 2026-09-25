import json


class Evaluator:

    def __init__(self, client, model):
        self.client = client
        self.model = model

    def evaluate(
        self,
        question,
        answer,
        research_context=""
    ):

        prompt = f"""
You are AURA's evaluation module.

Evaluate the quality of an AI-generated answer.

User question:
{question}

AI answer:
{answer}

Research context:
{research_context}

Evaluate the answer using these criteria:

1. factual_grounding
2. relevance
3. completeness
4. source_support
5. hallucination_risk

Return exactly one JSON object:

{{
    "factual_grounding": 0,
    "relevance": 0,
    "completeness": 0,
    "source_support": 0,
    "hallucination_risk": 0,
    "overall_score": 0,
    "explanation": ""
}}

Scoring:

- factual_grounding: 0-100
- relevance: 0-100
- completeness: 0-100
- source_support: 0-100
- hallucination_risk: 0-100
- overall_score: 0-100

For hallucination_risk:
0 means very low risk.
100 means very high risk.

Do not invent evidence.
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        text = response.output_text.strip()

        try:

            result = json.loads(
                text
            )

            numeric_fields = [
                "factual_grounding",
                "relevance",
                "completeness",
                "source_support",
                "hallucination_risk",
                "overall_score"
            ]

            for field in numeric_fields:

                value = int(
                    result.get(
                        field,
                        0
                    )
                )

                result[field] = max(
                    0,
                    min(
                        value,
                        100
                    )
                )

            return result

        except (
            json.JSONDecodeError,
            ValueError,
            TypeError
        ):

            return {
                "factual_grounding": 0,
                "relevance": 0,
                "completeness": 0,
                "source_support": 0,
                "hallucination_risk": 100,
                "overall_score": 0,
                "explanation": (
                    "Evaluation result "
                    "could not be parsed."
                )
            }