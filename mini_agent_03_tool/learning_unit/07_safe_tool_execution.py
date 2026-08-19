"""Allowlist 확인과 Schema 검증을 통과한 조회 Tool만 실행합니다."""

from datetime import date
from typing import Callable

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class WeatherInput(BaseModel):
    # LLM이 정의하지 않은 arguments를 끼워 넣어도 실행 전에 차단합니다.
    model_config = ConfigDict(extra="forbid")
    city: str = Field(min_length=1)
    target_date: date


def get_weather(arguments: dict) -> dict:
    # 실제 함수 안에서도 입력 계약을 다시 검증하는 방어 계층을 둡니다.
    args = WeatherInput.model_validate(arguments)
    return {"city": args.city, "date": args.target_date.isoformat(), "condition": "맑음", "source": "mock"}


# 실행 가능한 함수는 명시적 Allowlist에 등록된 조회 Tool로 제한합니다.
TOOLS: dict[str, Callable[[dict], dict]] = {"get_weather": get_weather}


def run_tool(tool_name: str, arguments: dict) -> dict:
    # LLM이 제안한 이름을 getattr이나 eval로 직접 실행하지 않습니다.
    tool = TOOLS.get(tool_name)
    if tool is None:
        return {"success": False, "error": {"code": "TOOL_NOT_ALLOWED"}}
    try:
        # 이름 검사 후 Schema 검증을 포함한 Tool 함수를 호출합니다.
        return {"success": True, "data": tool(arguments)}
    except ValidationError as error:
        details = [
            {"field": ".".join(map(str, item["loc"])), "message": item["msg"]}
            for item in error.errors()
        ]
        return {"success": False, "error": {"code": "TOOL_VALIDATION_ERROR", "details": details}}
    except Exception as error:
        return {"success": False, "error": {"code": "TOOL_EXECUTION_ERROR", "message": str(error)}}


if __name__ == "__main__":
    print("정상:", run_tool("get_weather", {"city": "부산", "target_date": "2026-08-12"}))
    print("검증 실패:", run_tool("get_weather", {"city": "부산"}))
    print("Allowlist 차단:", run_tool("delete_database", {}))
