import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.assistant import AURA

from database.service import DatabaseService

from .dependencies import get_aura, get_db
from .schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    StatusResponse
)


router = APIRouter()


@router.get("/", response_model=StatusResponse)
def root():

    return {
        "service": "AURA API",
        "status": "online"
    }


@router.get(
    "/health",
    response_model=HealthResponse
)
def health():

    return {
        "status": "healthy",
        "service": "AURA API"
    }


@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest,
    aura: AURA = Depends(get_aura),
    db: Session = Depends(get_db)
):

    database = DatabaseService(db)

    start_time = time.perf_counter()

    agent_run = None

    try:

        user = database.get_or_create_user(
            request.user_name
        )

        if request.conversation_id is None:

            conversation = (
                database.create_conversation(
                    user_id=user.id,
                    title=request.message[:100]
                )
            )

        else:

            conversation = (
                database.get_conversation(
                    request.conversation_id
                )
            )

            if conversation is None:

                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found."
                )

            if conversation.user_id != user.id:

                raise HTTPException(
                    status_code=403,
                    detail=(
                        "Conversation does not "
                        "belong to this user."
                    )
                )

        database.create_message(
            conversation_id=conversation.id,
            role="user",
            content=request.message
        )

        agent_run = (
            database.create_agent_run(
                user_input=request.message,
                status="running"
            )
        )

        answer = aura.think(
            request.message
        )

        execution = (
            aura.get_last_execution()
        )

        evaluation = {}

        tool_executions = []

        trace_id = None

        if execution:

            evaluation = (
                execution.get(
                    "evaluation",
                    {}
                )
            )

            tool_executions = (
                execution.get(
                    "tool_executions",
                    []
                )
            )

            trace_id = (
                execution.get(
                    "trace_id"
                )
            )

        duration_ms = (
            time.perf_counter()
            - start_time
        ) * 1000

        agent_run.status = "success"

        agent_run.duration_ms = (
            duration_ms
        )

        database.create_message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer
        )

        for tool_execution in tool_executions:

            database.create_tool_execution(
                agent_run_id=agent_run.id,
                tool_name=
                    tool_execution.get(
                        "tool",
                        "unknown"
                    ),
                status=
                    tool_execution.get(
                        "status",
                        "unknown"
                    )
            )

        database.create_evaluation(
            agent_run_id=agent_run.id,
            overall_score=
                evaluation.get(
                    "overall_score"
                ),
            factual_grounding=
                evaluation.get(
                    "factual_grounding"
                ),
            relevance=
                evaluation.get(
                    "relevance"
                ),
            completeness=
                evaluation.get(
                    "completeness"
                ),
            hallucination_risk=
                evaluation.get(
                    "hallucination_risk"
                )
        )

        db.commit()

        db.refresh(
            agent_run
        )

        return ChatResponse(
            user_id=user.id,
            conversation_id=
                conversation.id,
            agent_run_id=
                agent_run.id,
            answer=answer,
            status="success"
        )

    except HTTPException:

        db.rollback()

        raise

    except Exception as error:

        db.rollback()

        if agent_run is not None:

            try:

                agent_run.status = "failed"

                agent_run.duration_ms = (
                    time.perf_counter()
                    - start_time
                ) * 1000

                db.add(agent_run)

                db.commit()

            except Exception:

                db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"AURA execution failed: "
                f"{str(error)}"
            )
        )