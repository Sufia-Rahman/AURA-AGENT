import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is missing. Add it to your .env file."
    )


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def initialize_database():
    from .models import (
        User,
        Conversation,
        Message,
        AgentRun,
        ToolExecution,
        Evaluation
    )

    Base.metadata.create_all(bind=engine)