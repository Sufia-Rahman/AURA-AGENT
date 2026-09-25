from .recovery_engine import RecoveryEngine


class Agent:

    def __init__(
        self,
        brain,
        tools,
        planner,
        memory=None,
        reflection_memory=None,
        long_term_memory=None,
        memory_manager=None,
        observability=None,
        guardrails=None
    ):

        self.brain = brain
        self.tools = tools
        self.planner = planner

        self.memory = memory
        self.reflection_memory = reflection_memory
        self.long_term_memory = long_term_memory
        self.memory_manager = memory_manager

        self.observability = observability
        self.guardrails = guardrails

        self.recovery = RecoveryEngine(
            max_retries=2,
            retry_delay=1.0
        )

    def _minimal_plan(self, user_input):

        return {
            "goal": user_input,
            "requires_research": False,
            "steps": [
                {
                    "step": 1,
                    "action":
                        "Answer the user's request directly.",
                    "purpose":
                        "Provide a useful response."
                }
            ]
        }

    def _reduced_research_plan(self, plan):

        steps = plan.get(
            "steps",
            []
        )

        if not steps:

            return {
                **plan,
                "steps": []
            }

        return {
            **plan,
            "steps": steps[:1]
        }

    def _conservative_validation(
        self,
        research_results
    ):

        return {
            "confidence": 0,
            "supported": False,
            "explanation":
                "Research validation was unavailable. "
                "Treat the available evidence conservatively."
        }

    def _fallback_synthesis(
        self,
        research_results
    ):

        return (
            "Use only the available research evidence "
            "and clearly preserve uncertainty."
        )

    def _fallback_answer(
        self,
        research_results
    ):

        if research_results:
            return str(
                research_results
            )

        return (
            "I could not complete the requested "
            "task reliably."
        )

    def _fallback_evaluation(self):

        return {
            "factual_grounding": 0,
            "relevance": 0,
            "completeness": 0,
            "source_support": 0,
            "hallucination_risk": 100,
            "overall_score": 0,
            "explanation":
                "Evaluation was unavailable."
        }

    def _recover(
        self,
        operation,
        operation_name,
        fallback=None
    ):

        return self.recovery.execute(
            operation=operation,
            operation_name=operation_name,
            fallback=fallback
        )

    def run(
        self,
        user_input,
        user_name=None,
        memory_summary=None
    ):

        if self.guardrails:

            validation = (
                self.guardrails.validate_input(
                    user_input
                )
            )

            if not validation["allowed"]:

                return {
                    "plan":
                        self._minimal_plan(
                            user_input
                        ),
                    "result": {
                        "answer":
                            validation["reason"],
                        "sources": []
                    },
                    "evaluation": {},
                    "trace_id": None,
                    "tool_executions": []
                }

        trace_id = None

        if self.observability:

            trace_id = (
                self.observability.start_trace(
                    user_input
                )
            )

        if hasattr(
            self.tools,
            "reset_execution_state"
        ):

            self.tools.reset_execution_state()

        if hasattr(
            self.tools,
            "set_execution_context"
        ):

            self.tools.set_execution_context(
                trace_id
            )

        try:

            planning = self._recover(
                operation=lambda:
                    self.planner.create_plan(
                        user_input
                    ),
                operation_name="planning",
                fallback=lambda:
                    self._minimal_plan(
                        user_input
                    )
            )

            plan = planning["result"]

            if not isinstance(
                plan,
                dict
            ):

                plan = self._minimal_plan(
                    user_input
                )

            research_context = ""

            if plan.get(
                "requires_research",
                False
            ):

                research = self._recover(
                    operation=lambda:
                        self._run_research(
                            plan
                        ),
                    operation_name="research",
                    fallback=lambda:
                        self._run_research(
                            self._reduced_research_plan(
                                plan
                            )
                        )
                )

                research_context = (
                    research["result"]
                )

            improvement_context = (
                "No improvement strategies available."
            )

            if self.reflection_memory:

                strategies = (
                    self.reflection_memory
                    .strategy_context()
                )

                if strategies:
                    improvement_context = strategies

            long_term_context = (
                "No relevant long-term memories available."
            )

            if self.long_term_memory:

                long_term_context = (
                    self.long_term_memory
                    .retrieve_context(
                        query=user_input,
                        top_k=5
                    )
                )

            answer_result = self._recover(
                operation=lambda:
                    self.brain.respond(
                        user_input=user_input,
                        user_name=user_name,
                        memory_summary=memory_summary,
                        tools=self.tools,
                        plan=plan,
                        research_context=research_context,
                        improvement_context=
                            improvement_context,
                        long_term_context=
                            long_term_context
                    ),
                operation_name="answer_generation",
                fallback=lambda:
                    {
                        "answer":
                            self._fallback_answer(
                                research_context
                            ),
                        "sources": []
                    }
            )

            result = answer_result["result"]

            if not isinstance(
                result,
                dict
            ):

                result = {
                    "answer": str(result),
                    "sources": []
                }

            answer = result.get(
                "answer",
                ""
            )

            evaluation = (
                self._fallback_evaluation()
            )

            if hasattr(
                self.brain,
                "client"
            ):

                try:

                    evaluation_result = (
                        self._recover(
                            operation=lambda:
                                self._evaluate(
                                    user_input,
                                    answer
                                ),
                            operation_name="evaluation",
                            fallback=
                                self._fallback_evaluation
                        )
                    )

                    evaluation = (
                        evaluation_result["result"]
                    )

                except Exception:

                    evaluation = (
                        self._fallback_evaluation()
                    )

            if self.memory_manager:

                try:

                    self._recover(
                        operation=lambda:
                            self._form_memory(
                                user_input,
                                answer
                            ),
                        operation_name="memory_formation",
                        fallback=lambda: []
                    )

                except Exception:
                    pass

            tool_executions = []

            if hasattr(
                self.tools,
                "get_execution_log"
            ):

                tool_executions = (
                    self.tools.get_execution_log()
                )

            if self.observability:

                self.observability.finish_trace(
                    trace_id,
                    status="success"
                )

            return {
                "plan": plan,
                "result": result,
                "evaluation": evaluation,
                "trace_id": trace_id,
                "tool_executions": tool_executions
            }

        except Exception as error:

            if self.observability:

                self.observability.finish_trace(
                    trace_id,
                    status="failed"
                )

            tool_executions = []

            if hasattr(
                self.tools,
                "get_execution_log"
            ):

                tool_executions = (
                    self.tools.get_execution_log()
                )

            return {
                "plan":
                    self._minimal_plan(
                        user_input
                    ),
                "result": {
                    "answer":
                        "AURA encountered an internal "
                        "execution error: "
                        f"{error}",
                    "sources": []
                },
                "evaluation":
                    self._fallback_evaluation(),
                "trace_id": trace_id,
                "tool_executions": tool_executions
            }

    def _run_research(self, plan):

        if hasattr(
            self.brain,
            "research_engine"
        ):

            return (
                self.brain.research_engine.run(
                    plan
                )
            )

        return (
            "Research engine is not available."
        )

    def _evaluate(
        self,
        question,
        answer
    ):

        if hasattr(
            self.brain,
            "evaluator"
        ):

            return (
                self.brain.evaluator.evaluate(
                    question=question,
                    answer=answer
                )
            )

        return self._fallback_evaluation()

    def _form_memory(
        self,
        user_input,
        answer
    ):

        if hasattr(
            self.brain,
            "memory_formation"
        ):

            return (
                self.brain.memory_formation.extract(
                    user_input=user_input,
                    answer=answer
                )
            )

        return []