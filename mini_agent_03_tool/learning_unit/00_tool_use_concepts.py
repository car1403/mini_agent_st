"""Python 함수, Tool Schema, Tool Call, Tool Result를 비교합니다."""

from pydantic import BaseModel, Field


class WeatherInput(BaseModel):
    # Tool Schema의 필수 입력 계약입니다. 빈 문자열은 Pydantic이 거부합니다.
    city: str = Field(min_length=1)


def get_weather(arguments: dict) -> dict:
    # LLM이 만든 arguments를 그대로 믿지 않고 실행 직전에 검증합니다.
    args = WeatherInput.model_validate(arguments)
    return {"city": args.city, "condition": "맑음", "source": "mock"}


if __name__ == "__main__":
    # Schema는 LLM에게 함수의 이름, 용도, 입력 모양을 알려주는 설명서입니다.
    tool_schema = {
        "name": "get_weather",
        "description": "도시의 교육용 날씨를 조회합니다.",
        "input_schema": WeatherInput.model_json_schema(),
    }
    # Tool Call은 LLM의 실행 '제안'이며 아직 Python 함수는 호출되지 않았습니다.
    tool_call = {"name": "get_weather", "arguments": {"city": "부산"}}
    # Backend가 제안을 승인하고 함수를 호출한 뒤에야 Tool Result가 생깁니다.
    tool_result = get_weather(tool_call["arguments"])

    print("1. Python 함수:", get_weather.__name__)
    print("2. Tool Schema:", tool_schema)
    print("3. Tool Call:", tool_call)
    print("4. Tool Result:", tool_result)
