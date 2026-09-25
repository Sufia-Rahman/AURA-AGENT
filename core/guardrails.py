class Guardrails:

    def __init__(
        self,
        max_execution_steps=12,
        max_research_steps=5,
        max_tool_calls=10
    ):

        self.max_execution_steps = max_execution_steps
        self.max_research_steps = max_research_steps
        self.max_tool_calls = max_tool_calls

        self.blocked_operations = {
            "delete_files",
            "format_disk",
            "execute_shell",
            "modify_system",
            "install_software",
            "send_money",
            "make_purchase"
        }

    def validate_input(self, user_input):

        if not isinstance(user_input, str):
            return {
                "allowed": False,
                "reason": "Input must be text."
            }

        user_input = user_input.strip()

        if not user_input:
            return {
                "allowed": False,
                "reason": "Empty input."
            }

        if len(user_input) > 10000:
            return {
                "allowed": False,
                "reason": (
                    "Input exceeds maximum "
                    "allowed length."
                )
            }

        return {
            "allowed": True,
            "reason": "Input accepted."
        }

    def is_operation_allowed(self, operation):

        return (
            operation
            not in self.blocked_operations
        )

    def check_execution_limit(self, execution_steps):

        return (
            execution_steps
            < self.max_execution_steps
        )

    def check_research_limit(self, research_steps):

        return (
            research_steps
            < self.max_research_steps
        )

    def check_tool_limit(self, tool_calls):

        return (
            tool_calls
            < self.max_tool_calls
        )

    def validate_operation(
        self,
        operation,
        execution_steps=0,
        research_steps=0,
        tool_calls=0
    ):

        if not self.is_operation_allowed(operation):
            return {
                "allowed": False,
                "reason": (
                    f"Operation '{operation}' "
                    "is blocked by AURA guardrails."
                )
            }

        if not self.check_execution_limit(
            execution_steps
        ):
            return {
                "allowed": False,
                "reason": (
                    "Maximum execution "
                    "step limit reached."
                )
            }

        if not self.check_research_limit(
            research_steps
        ):
            return {
                "allowed": False,
                "reason": (
                    "Maximum research "
                    "step limit reached."
                )
            }

        if not self.check_tool_limit(
            tool_calls
        ):
            return {
                "allowed": False,
                "reason": (
                    "Maximum tool-call "
                    "limit reached."
                )
            }

        return {
            "allowed": True,
            "reason": "Operation allowed."
        }

    def statistics(self):

        return {
            "max_execution_steps":
                self.max_execution_steps,

            "max_research_steps":
                self.max_research_steps,

            "max_tool_calls":
                self.max_tool_calls,

            "blocked_operations":
                sorted(
                    self.blocked_operations
                )
        }