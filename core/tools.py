import json
import re
from datetime import datetime

from .knowledge_tool import KnowledgeTool
from .tool_permissions import ToolPermissionManager


class ToolRegistry:

    def __init__(
        self,
        permission_manager=None,
        guardrails=None,
        observability=None
    ):

        self.knowledge = KnowledgeTool()

        self.permission_manager = (
            permission_manager
            or ToolPermissionManager()
        )

        self.guardrails = guardrails
        self.observability = observability

        self.execution_log = []

        self.execution_steps = 0
        self.research_steps = 0
        self.tool_calls = 0

        self.tools = {
            "calculator": self.calculator,
            "current_time": self.current_time,
            "current_date": self.current_date,
            "search_knowledge": self.knowledge.execute
        }

    def reset_execution_state(self):

        self.execution_log = []

        self.execution_steps = 0
        self.research_steps = 0
        self.tool_calls = 0

    def set_execution_context(
        self,
        trace_id=None
    ):

        self.trace_id = trace_id

    def definitions(self):

        return [
            {
                "type": "function",
                "name": "calculator",
                "description":
                    "Calculate a mathematical expression.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string"
                        }
                    },
                    "required": [
                        "expression"
                    ],
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "current_time",
                "description":
                    "Get the current local time.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            {
                "type": "function",
                "name": "current_date",
                "description":
                    "Get today's date.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "additionalProperties": False
                }
            },
            self.knowledge.definitions()[0]
        ]

    def execute(
        self,
        name,
        arguments,
        execution_steps=None,
        research_steps=None,
        tool_calls=None,
        trace_id=None
    ):

        if execution_steps is None:
            execution_steps = self.execution_steps

        if research_steps is None:
            research_steps = self.research_steps

        if tool_calls is None:
            tool_calls = self.tool_calls

        if trace_id is None:
            trace_id = getattr(
                self,
                "trace_id",
                None
            )

        permission = (
            self.permission_manager.check(name)
        )

        if not permission["allowed"]:

            record = {
                "tool": name,
                "status": "blocked",
                "reason": permission["reason"]
            }

            self.execution_log.append(record)

            return {
                "status": "blocked",
                "tool": name,
                "result": None,
                "reason": permission["reason"]
            }

        if self.guardrails:

            guardrail = (
                self.guardrails.validate_operation(
                    operation=name,
                    execution_steps=execution_steps,
                    research_steps=research_steps,
                    tool_calls=tool_calls
                )
            )

            if not guardrail["allowed"]:

                record = {
                    "tool": name,
                    "status": "blocked",
                    "reason": guardrail["reason"]
                }

                self.execution_log.append(record)

                return {
                    "status": "blocked",
                    "tool": name,
                    "result": None,
                    "reason": guardrail["reason"]
                }

        if name not in self.tools:

            record = {
                "tool": name,
                "status": "error",
                "reason": "Unknown tool."
            }

            self.execution_log.append(record)

            return {
                "status": "error",
                "tool": name,
                "result": None,
                "reason": "Unknown tool."
            }

        self.tool_calls += 1

        if name == "search_knowledge":
            self.research_steps += 1

        step_id = None

        if self.observability and trace_id:

            step_id = (
                self.observability.start_step(
                    trace_id,
                    f"tool:{name}"
                )
            )

        started_at = datetime.now()

        try:

            if isinstance(arguments, str):

                arguments = json.loads(arguments)

            if not isinstance(arguments, dict):

                raise ValueError(
                    "Invalid tool arguments."
                )

            result = self.tools[name](
                **arguments
            )

            duration_ms = (
                datetime.now() - started_at
            ).total_seconds() * 1000

            if (
                self.observability
                and trace_id
                and step_id
            ):

                self.observability.finish_step(
                    trace_id,
                    step_id,
                    status="success",
                    metadata={
                        "tool": name,
                        "duration_ms":
                            round(duration_ms, 2)
                    }
                )

            record = {
                "tool": name,
                "status": "success",
                "duration_ms":
                    round(duration_ms, 2)
            }

            self.execution_log.append(record)

            return {
                "status": "success",
                "tool": name,
                "result": result,
                "reason":
                    "Tool executed successfully."
            }

        except Exception as error:

            duration_ms = (
                datetime.now() - started_at
            ).total_seconds() * 1000

            if (
                self.observability
                and trace_id
                and step_id
            ):

                self.observability.finish_step(
                    trace_id,
                    step_id,
                    status="failed",
                    metadata={
                        "tool": name,
                        "error": str(error),
                        "duration_ms":
                            round(duration_ms, 2)
                    }
                )

            record = {
                "tool": name,
                "status": "error",
                "error": str(error),
                "duration_ms":
                    round(duration_ms, 2)
            }

            self.execution_log.append(record)

            return {
                "status": "error",
                "tool": name,
                "result": None,
                "reason": str(error)
            }

    def get_execution_log(self):

        return list(
            self.execution_log
        )

    def statistics(self):

        successful = sum(
            1
            for item in self.execution_log
            if item["status"] == "success"
        )

        failed = sum(
            1
            for item in self.execution_log
            if item["status"] == "error"
        )

        blocked = sum(
            1
            for item in self.execution_log
            if item["status"] == "blocked"
        )

        return {
            "total_tool_calls":
                self.tool_calls,
            "successful":
                successful,
            "failed":
                failed,
            "blocked":
                blocked,
            "research_steps":
                self.research_steps
        }

    @staticmethod
    def calculator(expression):

        if not isinstance(
            expression,
            str
        ):

            raise ValueError(
                "Invalid mathematical expression."
            )

        if not re.fullmatch(
            r"[0-9+\-*/().%\s]+",
            expression
        ):

            raise ValueError(
                "Invalid mathematical expression."
            )

        try:

            result = eval(
                expression,
                {
                    "__builtins__": {}
                },
                {}
            )

            return str(result)

        except Exception as error:

            raise ValueError(
                "Unable to calculate "
                "the expression."
            ) from error

    @staticmethod
    def current_time():

        return datetime.now().strftime(
            "%I:%M %p"
        )

    @staticmethod
    def current_date():

        return datetime.now().strftime(
            "%d %B %Y"
        )

    def permission_report(self):

        return (
            self.permission_manager
            .statistics()
        )