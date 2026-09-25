from sqlalchemy.orm import Session

from .models import (
    AgentRun,
    Conversation,
    Evaluation,
    Message,
    ToolExecution,
    User
)


class UserRepository:

    @staticmethod
    def create(
        db: Session,
        name: str
    ):
        user = User(name=name)

        db.add(user)
        db.commit()
        db.refresh(user)

        return user


class ConversationRepository:

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        title: str | None = None
    ):
        conversation = Conversation(
            user_id=user_id,
            title=title
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation


class MessageRepository:

    @staticmethod
    def create(
        db: Session,
        conversation_id: int,
        role: str,
        content: str
    ):
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message


class AgentRunRepository:

    @staticmethod
    def create(
        db: Session,
        user_input: str,
        status: str,
        duration_ms: float | None = None
    ):
        run = AgentRun(
            user_input=user_input,
            status=status,
            duration_ms=duration_ms
        )

        db.add(run)
        db.commit()
        db.refresh(run)

        return run


class ToolExecutionRepository:

    @staticmethod
    def create(
        db: Session,
        agent_run_id: int,
        tool_name: str,
        status: str
    ):
        execution = ToolExecution(
            agent_run_id=agent_run_id,
            tool_name=tool_name,
            status=status
        )

        db.add(execution)
        db.commit()
        db.refresh(execution)

        return execution


class EvaluationRepository:

    @staticmethod
    def create(
        db: Session,
        agent_run_id: int,
        overall_score: float | None = None,
        factual_grounding: float | None = None,
        relevance: float | None = None,
        completeness: float | None = None,
        hallucination_risk: float | None = None
    ):
        evaluation = Evaluation(
            agent_run_id=agent_run_id,
            overall_score=overall_score,
            factual_grounding=factual_grounding,
            relevance=relevance,
            completeness=completeness,
            hallucination_risk=hallucination_risk
        )

        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)

        return evaluation