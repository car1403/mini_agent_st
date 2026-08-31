"""8010 포트에서 여행 Tool을 제공하는 Streamable HTTP MCP Server입니다."""

import os

from mcp.server.fastmcp import FastMCP


MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8010"))

mcp = FastMCP(
    "mini-agent-06-travel",
    instructions="한국 도시의 날씨와 날씨에 맞는 장소를 제공하는 교육용 Tool Server입니다.",
    host=MCP_HOST,
    port=MCP_PORT,
    stateless_http=True,
    json_response=True,
)

WEATHER = {
    "서울": {"condition": "맑음", "temperature_c": 24},
    "제주": {"condition": "비", "temperature_c": 21},
}
INDOOR = {"서울": ["국립중앙박물관", "서울시립미술관"], "제주": ["제주현대미술관", "아쿠아플라넷"]}
OUTDOOR = {"서울": ["서울숲", "북한산"], "제주": ["비자림", "성산일출봉"]}


@mcp.tool()
def get_weather(city: str) -> dict:
    """한국 도시의 현재 날씨를 조회합니다. 장소 추천 전에 먼저 사용합니다."""
    normalized = city.strip()
    if not normalized:
        raise ValueError("city는 빈 문자열일 수 없습니다.")
    data = WEATHER.get(normalized)
    if data is None:
        return {"success": False, "error": "CITY_NOT_FOUND", "city": normalized}
    return {"success": True, "city": normalized, **data, "source": "travel-mcp-server"}


@mcp.tool()
def search_indoor_places(city: str) -> dict:
    """비 오는 날에 방문하기 좋은 실내 장소를 검색합니다."""
    normalized = city.strip()
    if not normalized:
        raise ValueError("city는 빈 문자열일 수 없습니다.")
    return {"success": True, "city": normalized, "category": "indoor", "items": INDOOR.get(normalized, [])}


@mcp.tool()
def search_outdoor_places(city: str) -> dict:
    """맑은 날에 방문하기 좋은 야외 장소를 검색합니다."""
    normalized = city.strip()
    if not normalized:
        raise ValueError("city는 빈 문자열일 수 없습니다.")
    return {"success": True, "city": normalized, "category": "outdoor", "items": OUTDOOR.get(normalized, [])}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
