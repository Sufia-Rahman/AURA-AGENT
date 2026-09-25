from .ai_brain import AIBrain
from .config import Config
from .memory import Memory
from .tools import ToolRegistry
from .agent import Agent
from .planner import Planner
from .research_memory import ResearchMemory
from .knowledge_ingestion import KnowledgeIngestion
from .evaluation_memory import EvaluationMemory
from .performance_monitor import PerformanceMonitor
from .reflection_memory import ReflectionMemory
from .reflection_engine import ReflectionEngine
from .long_term_memory import LongTermMemory
from .memory_manager import MemoryManager
from .observability import Observability
from .guardrails import Guardrails
from .tool_permissions import ToolPermissionManager


class AURA:

    def __init__(self):

        self.config = Config()

        self.memory = Memory()
        self.research_memory = ResearchMemory()
        self.evaluation_memory = EvaluationMemory()

        self.performance_monitor = (
            PerformanceMonitor(
                self.evaluation_memory
            )
        )

        self.reflection_memory = (
            ReflectionMemory()
        )

        self.long_term_memory = (
            LongTermMemory()
        )

        self.memory_manager = (
            MemoryManager(
                long_term_memory=
                    self.long_term_memory
            )
        )

        self.observability = (
            Observability()
        )

        self.guardrails = (
            Guardrails()
        )

        self.tool_permission_manager = (
            ToolPermissionManager()
        )

        self.knowledge_ingestion = (
            KnowledgeIngestion()
        )

        self.brain = AIBrain()

        self.tools = ToolRegistry(
            permission_manager=
                self.tool_permission_manager,
            guardrails=
                self.guardrails,
            observability=
                self.observability
        )

        self.planner = Planner(
            client=self.brain.client,
            model=self.brain.model
        )

        self.reflection_engine = (
            ReflectionEngine(
                client=self.brain.client,
                model=self.brain.model
            )
        )

        self.agent = Agent(
            brain=self.brain,
            tools=self.tools,
            planner=self.planner,
            memory=self.memory,
            reflection_memory=
                self.reflection_memory,
            long_term_memory=
                self.long_term_memory,
            memory_manager=
                self.memory_manager,
            observability=
                self.observability,
            guardrails=
                self.guardrails
        )

        self.last_execution = None

        self.knowledge_ingestion.ingest_new_documents()

    def think(self, user_input):

        execution = self.agent.run(
            user_input=user_input,
            user_name=self.memory.get_name(),
            memory_summary=self.memory.summary
        )

        self.last_execution = execution

        plan = execution["plan"]
        result = execution["result"]

        answer = result["answer"]
        sources = result["sources"]

        evaluation = execution.get(
            "evaluation",
            {}
        )

        self.memory.add_history(
            user_input,
            answer
        )

        self.evaluation_memory.add_record(
            question=user_input,
            answer=answer,
            evaluation=evaluation
        )

        if plan.get(
            "requires_research",
            False
        ):

            self.research_memory.add_record(
                query=user_input,
                plan=plan,
                answer=answer,
                sources=sources
            )

        return answer

    def get_last_execution(self):

        return self.last_execution

    def performance_report(self):

        return (
            self.performance_monitor.report()
        )

    def reflect_on_performance(self):

        performance_report = (
            self.performance_monitor.report()
        )

        recent_evaluations = (
            self.evaluation_memory.recent(
                limit=10
            )
        )

        reflection = (
            self.reflection_engine.reflect(
                performance_report=
                    performance_report,
                recent_evaluations=
                    recent_evaluations
            )
        )

        self.reflection_memory.add_record(
            reflection
        )

        return reflection

    def memory_report(self):

        return (
            self.long_term_memory.statistics()
        )

    def memory_manager_report(self):

        return (
            self.memory_manager.statistics()
        )

    def observability_report(self):

        return (
            self.observability.statistics()
        )

    def recovery_report(self):

        return (
            self.agent.recovery.statistics()
        )

    def guardrails_report(self):

        return (
            self.guardrails.statistics()
        )

    def tool_permission_report(self):

        return (
            self.tool_permission_manager.statistics()
        )

    def tool_execution_report(self):

        return (
            self.tools.statistics()
        )