class FallbackEngine:

    def __init__(self):

        self.strategies = {
            "planning": [
                "simplify_plan",
                "direct_execution"
            ],

            "research": [
                "reduce_research_scope",
                "use_available_evidence"
            ],

            "research_validation": [
                "skip_validation",
                "use_conservative_validation"
            ],

            "research_synthesis": [
                "use_available_evidence",
                "conservative_synthesis"
            ],

            "answer_generation": [
                "use_research_synthesis",
                "conservative_answer"
            ],

            "evaluation": [
                "basic_quality_check",
                "skip_optional_evaluation"
            ],

            "memory_formation": [
                "skip_memory",
                "continue_without_memory"
            ]
        }

    def get_strategies(
        self,
        operation
    ):

        return self.strategies.get(
            operation,
            [
                "continue_without_optional_step"
            ]
        )

    def select(
        self,
        operation,
        failed_attempts=0
    ):

        options = self.get_strategies(
            operation
        )

        index = min(
            failed_attempts,
            len(options) - 1
        )

        return {
            "operation": operation,
            "strategy": options[index],
            "available_strategies": options
        }

    def describe(
        self,
        strategy
    ):

        descriptions = {

            "simplify_plan":
                "Create a smaller execution plan with fewer steps.",

            "direct_execution":
                "Skip complex planning and use a minimal execution path.",

            "reduce_research_scope":
                "Reduce research to the most important planned step.",

            "use_available_evidence":
                "Continue using evidence already collected.",

            "skip_validation":
                "Skip optional research validation when validation is unavailable.",

            "use_conservative_validation":
                "Treat research evidence conservatively and preserve uncertainty.",

            "conservative_synthesis":
                "Synthesize only information supported by available evidence.",

            "use_research_synthesis":
                "Use the available research synthesis as the answer source.",

            "conservative_answer":
                "Generate a cautious answer using available context.",

            "basic_quality_check":
                "Use a lightweight local quality check.",

            "skip_optional_evaluation":
                "Continue without the optional evaluation stage.",

            "skip_memory":
                "Skip memory formation and continue the task.",

            "continue_without_memory":
                "Complete the task without creating new long-term memory.",

            "continue_without_optional_step":
                "Skip the failed optional operation safely."
        }

        return descriptions.get(
            strategy,
            "Use a safe alternative execution strategy."
        )

    def statistics(self):

        return {
            "operations":
                list(
                    self.strategies.keys()
                ),

            "total_strategies":
                sum(
                    len(items)
                    for items
                    in self.strategies.values()
                )
        }