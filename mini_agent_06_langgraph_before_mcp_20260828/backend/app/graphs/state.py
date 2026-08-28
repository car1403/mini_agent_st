from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    question: str
    previous_response_id: str
    pending_calls: list[Any]
    tool_outputs: list[dict[str, Any]]
    answer: str | None
    status: str
    termination_reason: str | None
    llm_calls: int
    tool_calls: int
    trace: list[dict[str, Any]]
