from typing import Any

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class AgentResponse(BaseModel):
    question: str
    model: str
    status: str
    termination_reason: str
    llm_calls: int
    tool_calls: int
    trace: list[dict[str, Any]]
    answer: str | None = None
