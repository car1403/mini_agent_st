"""외부 LLM 없이 질문을 분석해 교육용 Tool을 선택합니다.

`agents.tool_selector`가 Mock 모드의 Tool 결정에 사용합니다.
"""


def select_mock_tool(message: str) -> dict:
    if any(word in message for word in ("날씨", "비가", "비예보", "기온", "우산")):
        if any(word in message for word in ("내일", "모레", "주말", "예보", "다음 주")):
            return {"tool_name": "get_weather_forecast", "reason": "미래 날씨 예보 요청", "confidence": 0.94}
        return {"tool_name": "get_current_weather", "reason": "현재 날씨 요청", "confidence": 0.94}
    if any(word in message for word in ("호텔", "숙소", "체크인")):
        return {"tool_name": "search_hotels", "reason": "숙소 관련 요청", "confidence": 0.94}
    if any(word in message for word in ("관광지", "가볼", "명소")):
        return {"tool_name": "search_attractions", "reason": "관광지 관련 요청", "confidence": 0.9}
    return {"tool_name": None, "reason": "필요한 Tool을 확정할 수 없음", "confidence": 0.35}
