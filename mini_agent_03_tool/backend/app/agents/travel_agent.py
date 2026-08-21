"""여행 도메인 Agent의 역할·지침·Tool을 정의합니다."""

from datetime import date, timedelta
from typing import Any

from app.agents.runtime import ToolDecision, run_agent, select_tool
from app.schemas.stage_03 import ToolCompleteResult
from app.tools.registry import get_tool_definitions


TRAVEL_AGENT_NAME = "travel_lookup_agent"

TRAVEL_AGENT_INSTRUCTIONS = """
당신은 여행 조회 Agent입니다.
사용자의 질문을 해결하기 위해 필요한 경우 날씨, 숙소 또는 관광지 Tool 하나를 선택하세요.
필수 입력값이 부족하면 추측하지 말고, 허용된 Tool 외에는 선택하지 마세요.
""".strip()

TRAVEL_FINAL_ANSWER_INSTRUCTIONS = """
당신은 친절한 여행 도우미입니다.
Tool Result에 포함된 정보만 사용해 한국어로 답변하고, 결과에 없는 값은 추측하지 마세요.
""".strip()


def get_travel_tools() -> list[dict[str, Any]]:
    """여행 Agent가 사용할 수 있는 Tool 목록입니다."""
    return get_tool_definitions()


def select_travel_tool(
    provider: str,
    message: str,
    tool_choice: str = "auto",
) -> ToolDecision:
    """여행 Agent의 지침과 Tool을 사용해 실행할 Tool을 선택합니다."""
    return select_tool(
        provider=provider,
        message=message,
        instructions=TRAVEL_AGENT_INSTRUCTIONS,
        tools=get_travel_tools(),
        mock_selector=_select_travel_tool_with_mock,
        tool_choice=tool_choice,
    )


def run_travel_agent(
    provider: str,
    message: str,
    tool_choice: str = "auto",
) -> ToolCompleteResult:
    """여행 질문을 Tool 선택 → 실행 → 최종 답변 순서로 처리합니다."""
    return run_agent(
        provider=provider,
        message=message,
        instructions=TRAVEL_AGENT_INSTRUCTIONS,
        final_answer_instructions=TRAVEL_FINAL_ANSWER_INSTRUCTIONS,
        tools=get_travel_tools(),
        mock_selector=_select_travel_tool_with_mock,
        tool_choice=tool_choice,
    )


def _select_travel_tool_with_mock(message: str, tool_choice: str) -> ToolDecision:
    """API 키 없이 여행 Agent의 판단을 연습하는 결정론적 Mock입니다."""
    if any(word in message for word in ("날씨", "비가", "비예보", "기온", "우산")):
        tool_name = "get_weather_forecast" if any(word in message for word in ("내일", "주말", "예보")) else "get_current_weather"
    elif any(word in message for word in ("숙소", "호텔")):
        tool_name = "search_hotels"
    elif any(word in message for word in ("관광", "명소", "가볼")):
        tool_name = "search_attractions"
    else:
        tool_name = None

    if tool_choice == "required" and tool_name is None:
        tool_name = "get_current_weather"

    city = next((name for name in ("서울", "부산", "제주", "강릉") if name in message), None)
    arguments: dict[str, Any] = {}
    if tool_name == "get_current_weather" and city:
        arguments = {"city": city}
    elif tool_name == "get_weather_forecast":
        target_date = (date.today() + timedelta(days=1)).isoformat() if "내일" in message else None
        arguments = {key: value for key, value in {"city": city, "target_date": target_date}.items() if value is not None}
    elif tool_name == "search_hotels" and city:
        arguments = {"city": city}
    elif tool_name == "search_attractions":
        arguments = {"category": "all", **({"city": city} if city else {})}

    return ToolDecision(
        provider="mock",
        model="deterministic-travel-mock",
        tool_name=tool_name,
        arguments=arguments,
        reason="여행 질문의 핵심 단어와 Tool 설명을 비교한 Mock 결과",
        confidence=0.9 if tool_name else 0.4,
        latency_ms=0,
        raw_tool_call={"name": tool_name, "arguments": arguments} if tool_name else None,
    )
