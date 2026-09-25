from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .connection import Base


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Conversation(Base):

    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    title: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


class Message(Base):

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id"),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )


class AgentRun(Base):

    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_input: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    duration_ms: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class ToolExecution(Base):

    __tablename__ = "tool_executions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    agent_run_id: Mapped[int] = mapped_column(
        ForeignKey("agent_runs.id"),
        nullable=False
    )

    tool_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class Evaluation(Base):

    __tablename__ = "evaluations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    agent_run_id: Mapped[int] = mapped_column(
        ForeignKey("agent_runs.id"),
        nullable=False
    )

    overall_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    factual_grounding: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    relevance: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    completeness: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    hallucination_risk: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )