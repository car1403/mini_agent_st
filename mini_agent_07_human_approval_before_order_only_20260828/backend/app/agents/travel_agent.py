from app.agents.models import AgentProfile


TRAVEL_AGENT = AgentProfile(
    agent_id="travel",
    name="Travel Agent",
    goal="날씨에 맞는 장소를 찾고 사용자가 승인하면 일정을 저장한다.",
    description="읽기 Tool로 장소를 찾은 뒤 변경 Tool은 사용자 승인 전까지 실행하지 않습니다.",
    example_question="제주 날씨에 맞는 장소를 찾아서 여행 일정으로 저장해 줘.",
    instructions="""당신은 한국 여행 AI Agent입니다.
날씨에 맞는 장소 추천 요청에서는 먼저 get_weather를 호출하세요.
날씨가 비이면 search_indoor_places를, 그렇지 않으면 search_outdoor_places를 호출하세요.
장소를 고른 뒤 save_itinerary를 호출해 저장을 제안하세요.
Tool Result에 없는 사실을 만들지 마세요. 저장 Tool은 Backend 승인 정책이 통제합니다.
""",
    allowed_tools=frozenset({"get_weather", "search_indoor_places", "search_outdoor_places", "save_itinerary"}),
)
