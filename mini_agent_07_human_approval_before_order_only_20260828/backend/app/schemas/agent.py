from typing import Any, Literal

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    agent_id: str
    actor_id: str = Field(min_length=1, max_length=100)
    question: str = Field(min_length=1, max_length=500)


class ApprovalDecision(BaseModel):
    actor_id: str = Field(min_length=1, max_length=100)
    decision: Literal["approve", "reject"]
    approval_target: dict[str, Any]
    note: str = Field(default="", max_length=500)


class AgentSummary(BaseModel):
    agent_id: str
    name: str
    goal: str
    description: str
    example_question: str
    allowed_tools: list[str]


class AgentResponse(BaseModel):
    run_id: str
    agent_id: str
    agent_name: str
    goal: str
    actor_id: str
    question: str
    model: str
    status: str
    termination_reason: str | None
    llm_calls: int
    tool_calls: int
    trace: list[dict[str, Any]]
    answer: str | None = None
    pending_approval: dict[str, Any] | None = None
