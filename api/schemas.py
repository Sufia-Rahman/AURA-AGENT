from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_name: str = Field(default="User", min_length=1, max_length=255)
    message: str = Field(min_length=1, max_length=10000)
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    user_id: int
    conversation_id: int
    agent_run_id: int
    answer: str
    status: str


class HealthResponse(BaseModel):
    status: str
    service: str


class StatusResponse(BaseModel):
    service: str
    status: str