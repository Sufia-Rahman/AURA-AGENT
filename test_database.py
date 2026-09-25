from database.connection import SessionLocal, initialize_database
from database.service import DatabaseService


initialize_database()

db = SessionLocal()

try:
    service = DatabaseService(db)

    user = service.create_user(
        "AURA Test User"
    )

    conversation = service.create_conversation(
        user_id=user.id,
        title="AURA PostgreSQL Test"
    )

    message = service.create_message(
        conversation_id=conversation.id,
        role="user",
        content="Testing AURA PostgreSQL integration."
    )

    run = service.create_agent_run(
        user_input="Testing database persistence.",
        status="success"
    )

    evaluation = service.create_evaluation(
        agent_run_id=run.id,
        overall_score=95,
        factual_grounding=95,
        relevance=96,
        completeness=94,
        hallucination_risk=5
    )

    print("DATABASE CONNECTION: SUCCESS")
    print("User ID:", user.id)
    print("Conversation ID:", conversation.id)
    print("Message ID:", message.id)
    print("Agent Run ID:", run.id)
    print("Evaluation ID:", evaluation.id)

finally:
    db.close()