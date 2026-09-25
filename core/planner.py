import json


class Planner:

    def __init__(self, client, model):
        self.client = client
        self.model = model

    def create_plan(self, user_input):

        response = self.client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are the planning module of AURA, "
                        "an autonomous research and reasoning agent. "
                        "Analyze the user's goal and create a practical "
                        "execution plan. Do not answer the task itself."
                    )
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "aura_task_plan",
                    "description": (
                        "A structured execution plan for an agent task."
                    ),
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "goal": {
                                "type": "string"
                            },
                            "requires_research": {
                                "type": "boolean"
                            },
                            "steps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "step": {
                                            "type": "integer"
                                        },
                                        "action": {
                                            "type": "string"
                                        },
                                        "purpose": {
                                            "type": "string"
                                        }
                                    },
                                    "required": [
                                        "step",
                                        "action",
                                        "purpose"
                                    ],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": [
                            "goal",
                            "requires_research",
                            "steps"
                        ],
                        "additionalProperties": False
                    }
                }
            }
        )

        return json.loads(
            response.output_text
        )