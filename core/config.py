import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "AURA"
MODEL_NAME = "AURA-Core"

MEMORY_FILE = os.getenv(
    "MEMORY_FILE",
    "memory.json"
)

MAX_CONVERSATIONS = int(
    os.getenv(
        "MAX_CONVERSATIONS",
        "100"
    )
)

API_KEY = os.getenv(
    "API_KEY",
    ""
)

DEBUG = os.getenv(
    "DEBUG",
    "False"
).lower() == "true"
class Config:
    MEMORY_FILE = MEMORY_FILE
    MAX_CONVERSATIONS = MAX_CONVERSATIONS
    API_KEY = API_KEY
    DEBUG = DEBUG