class ToolPermissionManager:

    def __init__(self):

        self.permissions = {
            "calculator": True,
            "current_time": True,
            "current_date": True,
            "search_knowledge": True
        }

    def is_allowed(
        self,
        tool_name
    ):

        return self.permissions.get(
            tool_name,
            False
        )

    def check(
        self,
        tool_name
    ):

        if self.is_allowed(tool_name):

            return {
                "allowed": True,
                "tool": tool_name,
                "reason": "Tool is permitted."
            }

        return {
            "allowed": False,
            "tool": tool_name,
            "reason": (
                f"Tool '{tool_name}' "
                "is not permitted."
            )
        }

    def allow(
        self,
        tool_name
    ):

        self.permissions[tool_name] = True

    def deny(
        self,
        tool_name
    ):

        self.permissions[tool_name] = False

    def statistics(self):

        allowed = [
            tool
            for tool, enabled
            in self.permissions.items()
            if enabled
        ]

        denied = [
            tool
            for tool, enabled
            in self.permissions.items()
            if not enabled
        ]

        return {
            "allowed_tools": allowed,
            "denied_tools": denied,
            "total_tools": len(
                self.permissions
            )
        }