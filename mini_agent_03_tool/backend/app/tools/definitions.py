from app.schemas import AttractionArgs, HotelArgs, WeatherArgs


TRAVEL_TOOL_DEFINITIONS = [
    {"name": "get_weather", "description": "특정 도시와 날짜의 교육용 날씨를 조회합니다.", "input_schema": WeatherArgs.model_json_schema()},
    {"name": "search_hotels", "description": "도시, 날짜, 인원에 맞는 교육용 숙소를 조회합니다.", "input_schema": HotelArgs.model_json_schema()},
    {"name": "search_attractions", "description": "도시와 분류에 맞는 교육용 관광지를 조회합니다.", "input_schema": AttractionArgs.model_json_schema()},
]

VAGUE_TOOL_DEFINITIONS = [
    {"name": item["name"], "description": "여행 정보를 조회합니다.", "input_schema": item["input_schema"]}
    for item in TRAVEL_TOOL_DEFINITIONS
]


def get_tool_definitions(variant: str = "clear") -> list[dict]:
    """설명 품질만 바꿔 LLM의 Tool 선택 차이를 실험합니다."""
    if variant == "clear":
        return TRAVEL_TOOL_DEFINITIONS
    if variant == "vague":
        return VAGUE_TOOL_DEFINITIONS
    raise ValueError(f"지원하지 않는 Tool 설명 유형입니다: {variant}")
