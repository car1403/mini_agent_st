import json
from typing import Any, Callable

from app.tools.travel import get_weather, search_indoor_places, search_outdoor_places


TOOL_FUNCTIONS: dict[str, Callable[[str], dict[str, Any]]] = {
    "get_weather": get_weather,
    "search_indoor_places": search_indoor_places,
    "search_outdoor_places": search_outdoor_places,
}

TOOL_DESCRIPTIONS = {
    "get_weather": "한국 도시의 현재 날씨를 조회합니다.",
    "search_indoor_places": "비 오는 날에 적합한 실내 장소를 검색합니다.",
    "search_outdoor_places": "맑은 날에 적합한 야외 장소를 검색합니다.",
}

OPENAI_TOOLS = [
    {
        "type": "function",
        "name": name,
        "description": TOOL_DESCRIPTIONS[name],
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "한국 도시 이름"}},
            "required": ["city"],
            "additionalProperties": False,
        },
        "strict": True,
    }
    for name in TOOL_FUNCTIONS
]


def execute_call(call: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    if call.name not in TOOL_FUNCTIONS:
        raise ValueError(f"허용되지 않은 Tool입니다: {call.name}")
    arguments = json.loads(call.arguments)
    city = arguments.get("city")
    if not isinstance(city, str) or not city.strip():
        raise ValueError("city는 비어 있지 않은 문자열이어야 합니다.")
    result = TOOL_FUNCTIONS[call.name](city.strip())
    output = {
        "type": "function_call_output",
        "call_id": call.call_id,
        "output": json.dumps(result, ensure_ascii=False),
    }
    trace = {"tool": call.name, "arguments": {"city": city.strip()}, "result": result}
    return output, trace
