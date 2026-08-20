"""질문과 Tool 목록을 Provider에 전달하고 최종 Tool 결정을 만듭니다.

Stage 03 라우터와 `agents.tool_loop.run_tool_agent()`가 Agent의 판단 단계에서 사용합니다.
"""

from datetime import date, timedelta
from typing import Any

from app.agents.argument_resolver import resolve_arguments
from app.agents.mock_selector import select_mock_tool
from app.agents.models import ToolDecision
from app.providers.models import ProviderToolCall
from app.providers.registry import get_provider
from app.tools.registry import get_tool_definitions


def decide_tool(provider: str, message: str, tool_choice: str = "auto") -> ToolDecision:
    selected_provider = get_provider(provider)
    if tool_choice == "none":
        return ToolDecision(provider, "tool-choice-none", None, {}, "Tool 사용 금지", 1.0, 0)
    if provider == "mock":
        call = _select_mock(message, tool_choice)
    else:
        call = selected_provider.select_tool(message, get_tool_definitions(), tool_choice)
    return resolve_arguments(call)


def _select_mock(message: str, tool_choice: str) -> ProviderToolCall:
    decision = select_mock_tool(message)
    if tool_choice == "required" and decision["tool_name"] is None:
        decision = {"tool_name": "get_current_weather", "reason": "Tool 사용 필수 모드", "confidence": 0.5}
    tool_name = decision["tool_name"]
    arguments: dict[str, Any] = {}
    city = next((name for name in ("서울", "부산", "제주", "강릉") if name in message), None)
    if tool_name == "get_current_weather" and city:
        arguments = {"city": city}
    elif tool_name == "get_weather_forecast":
        target_date = (date.today() + timedelta(days=1)).isoformat() if "내일" in message else None
        arguments = {key: value for key, value in {"city": city, "target_date": target_date}.items() if value is not None}
    elif tool_name == "search_hotels" and city:
        arguments = {"city": city}
    elif tool_name == "search_attractions":
        arguments = {"category": "all", **({"city": city} if city else {})}
    return ProviderToolCall("mock", "deterministic-travel-mock", tool_name, arguments, decision["reason"], decision["confidence"], 0, {"name": tool_name, "arguments": arguments} if tool_name else None)
