import json


class ReflectionEngine:

    def __init__(self, client, model):

        self.client = client
        self.model = model

    def reflect(
        self,
        performance_report,
        recent_evaluations
    ):

        prompt = f"""
You are AURA's reflection module.

Your job is to analyze AURA's past performance and
create a controlled improvement strategy.

Performance report:
{performance_report}

Recent evaluations:
{recent_evaluations}

Analyze:

1. recurring weaknesses
2. possible failure patterns
3. likely causes
4. practical improvement strategy

Do not modify code.
Do not invent evidence.
Do not claim that AURA improved unless the data supports it.

Return exactly one JSON object:

{{
    "failure_pattern": "",
    "likely_cause": "",
    "improvement_strategy": "",
    "expected_effect": ""
}}
"""

        response = self.client.responses.create(
            model=self.model,
            input=prompt
        )

        text = response.output_text.strip()

        try:

            result = json.loads(text)

            return {
                "failure_pattern": result.get(
                    "failure_pattern",
                    ""
                ),
                "likely_cause": result.get(
                    "likely_cause",
                    ""
                ),
                "improvement_strategy": result.get(
                    "improvement_strategy",
                    ""
                ),
                "expected_effect": result.get(
                    "expected_effect",
                    ""
                )
            }

        except (
            json.JSONDecodeError,
            TypeError
        ):

            return {
                "failure_pattern": "",
                "likely_cause": "",
                "improvement_strategy": "",
                "expected_effect": "",
                "error": "Reflection result could not be parsed."
            }