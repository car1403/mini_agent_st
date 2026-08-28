from typing import Any


WEATHER = {
    "서울": {"condition": "맑음", "temperature_c": 24},
    "제주": {"condition": "비", "temperature_c": 21},
}
INDOOR = {"서울": ["국립중앙박물관", "서울시립미술관"], "제주": ["제주현대미술관", "아쿠아플라넷"]}
OUTDOOR = {"서울": ["서울숲", "북한산"], "제주": ["비자림", "성산일출봉"]}


def get_weather(city: str) -> dict[str, Any]:
    data = WEATHER.get(city)
    if data is None:
        return {"success": False, "error": "CITY_NOT_FOUND", "city": city}
    return {"success": True, "city": city, **data, "source": "local-learning-data"}


def search_indoor_places(city: str) -> dict[str, Any]:
    return {"success": True, "city": city, "category": "indoor", "items": INDOOR.get(city, [])}


def search_outdoor_places(city: str) -> dict[str, Any]:
    return {"success": True, "city": city, "category": "outdoor", "items": OUTDOOR.get(city, [])}
