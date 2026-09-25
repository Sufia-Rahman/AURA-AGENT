from database.connection import SessionLocal
from core.assistant import AURA


aura = AURA()


def get_aura():
    return aura


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()