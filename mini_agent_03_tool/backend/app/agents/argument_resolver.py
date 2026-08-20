"""선택된 Tool의 필수 인자를 검사하고 사용자 추가 질문을 구성합니다.

`agents.tool_selector.decide_tool()`이 Provider 응답을 최종 Agent 판단으로 바꿀 때 사용합니다.
"""

from app.agents.models import ToolDecision
from app.providers.models import ProviderToolCall
from app.tools.registry import get_tool_definitions


def resolve_arguments(call: ProviderToolCall) -> ToolDecision:
    definitions = {tool["name"]: tool for tool in get_tool_definitions()}
    schema = definitions.get(call.tool_name or "", {}).get("input_schema", {})
    missing = [name for name in schema.get("required", []) if name not in call.arguments]
    return ToolDecision(
        provider=call.provider,
        model=call.model,
        tool_name=call.tool_name,
        arguments=call.arguments,
        reason=call.reason,
        confidence=call.confidence,
        latency_ms=call.latency_ms,
        missing_arguments=missing,
        needs_clarification=bool(missing),
        follow_up_question=f"Tool 실행 전에 다음 정보를 알려주세요: {', '.join(missing)}" if missing else "",
        raw_tool_call=call.raw_tool_call,
    )
