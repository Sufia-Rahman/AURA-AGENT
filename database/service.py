from sqlalchemy.orm import Session

from .models import Conversation, User

from .repositories import (
    AgentRunRepository,
    ConversationRepository,
    EvaluationRepository,
    MessageRepository,
    ToolExecutionRepository,
    UserRepository
)


class DatabaseService:

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_name(self, name: str):
        return (
            self.db.query(User)
            .filter(User.name == name)
            .first()
        )

    def get_or_create_user(self, name: str):
        user = self.get_user_by_name(name)

        if user:
            return user

        return UserRepository.create(
            self.db,
            name
        )

    def create_conversation(
        self,
        user_id: int,
        title: str | None = None
    ):
        return ConversationRepository.create(
            self.db,
            user_id,
            title
        )

    def get_conversation(self, conversation_id: int):
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

    def create_message(
        self,
        conversation_id: int,
        role: str,
        content: str
    ):
        return MessageRepository.create(
            self.db,
            conversation_id,
            role,
            content
        )

    def create_agent_run(
        self,
        user_input: str,
        status: str,
        duration_ms: float | None = None
    ):
        return AgentRunRepository.create(
            self.db,
            user_input,
            status,
            duration_ms
        )

    def create_tool_execution(
        self,
        agent_run_id: int,
        tool_name: str,
        status: str
    ):
        return ToolExecutionRepository.create(
            self.db,
            agent_run_id,
            tool_name,
            status
        )

    def create_evaluation(
        self,
        agent_run_id: int,
        overall_score: float | None = None,
        factual_grounding: float | None = None,
        relevance: float | None = None,
        completeness: float | None = None,
        hallucination_risk: float | None = None
    ):
        return EvaluationRepository.create(
            self.db,
            agent_run_id,
            overall_score,
            factual_grounding,
            relevance,
            completeness,
            hallucination_risk
        )