from typing import Any

from openai import AsyncOpenAI

from app.core.config import OPENAI_MODEL, require_openai_api_key


INSTRUCTIONS = """당신은 한국 여행 AI Agent입니다.
사용자의 목표를 달성하기 위해 제공된 MCP Tool만 사용하세요.
날씨에 맞는 장소 추천 요청에서는 먼저 get_weather를 호출하세요.
날씨가 비이면 search_indoor_places를, 그렇지 않으면 search_outdoor_places를 호출하세요.
Tool Result에 없는 사실은 만들지 말고, 근거가 충분하면 간결한 한국어 답변을 작성하세요.
"""


def create_client() -> AsyncOpenAI:
    require_openai_api_key()
    return AsyncOpenAI()


async def create_response(client: AsyncOpenAI, question: str, tools: list[dict[str, Any]]) -> Any:
    return await client.responses.create(
        model=OPENAI_MODEL,
        instructions=INSTRUCTIONS,
        input=question,
        tools=tools,
        tool_choice="auto",
        parallel_tool_calls=False,
    )


async def continue_response(
    client: AsyncOpenAI,
    previous_response_id: str,
    tool_outputs: list[dict[str, Any]],
    tools: list[dict[str, Any]],
) -> Any:
    return await client.responses.create(
        model=OPENAI_MODEL,
        instructions=INSTRUCTIONS,
        previous_response_id=previous_response_id,
        input=tool_outputs,
        tools=tools,
        tool_choice="auto",
        parallel_tool_calls=False,
    )
