"""Agent 판단 과정에서 사용하는 내부 결과 모델입니다.

`agents.tool_selector`가 Provider Tool Call에 누락 인자와 후속 질문을 더해 반환합니다.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolDecision:
    provider: str
    model: str
    tool_name: str | None
    arguments: dict[str, Any]
    reason: str
    confidence: float
    latency_ms: int
    missing_arguments: list[str] = field(default_factory=list)
    needs_clarification: bool = False
    follow_up_question: str = ""
    raw_tool_call: dict[str, Any] | None = None
