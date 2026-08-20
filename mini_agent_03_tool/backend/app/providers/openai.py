"""OpenAI Responses API를 공통 Provider 계약으로 변환하는 어댑터입니다.

`providers.registry`가 생성하며 generation/structured services와 `agents.tool_selector`가 사용합니다.
"""

import json
from time import perf_counter
from typing import Any

from pydantic import BaseModel

from app.core.config import settings
from app.providers.models import ProviderResult, ProviderToolCall


class OpenAIProvider:
    name = "openai"

    def _client(self):
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        from openai import OpenAI

        return OpenAI(api_key=settings.openai_api_key)

    def generate(self, system_prompt: str, message: str) -> ProviderResult:
        started = perf_counter()
        response = self._client().responses.create(
            model=settings.openai_model, instructions=system_prompt, input=message
        )
        return ProviderResult(self.name, settings.openai_model, response.output_text, round((perf_counter() - started) * 1000))

    def generate_structured(self, system_prompt: str, message: str, response_schema: type[BaseModel]) -> ProviderResult:
        started = perf_counter()
        response = self._client().responses.parse(
            model=settings.openai_model, instructions=system_prompt, input=message, text_format=response_schema
        )
        if response.output_parsed is None:
            raise RuntimeError("OpenAI가 구조화된 결과를 반환하지 않았습니다.")
        return ProviderResult(self.name, settings.openai_model, response.output_parsed.model_dump(), round((perf_counter() - started) * 1000))

    def select_tool(self, message: str, tools: list[dict[str, Any]], tool_choice: str = "auto") -> ProviderToolCall:
        openai_tools = [
            {"type": "function", "name": tool["name"], "description": tool["description"], "parameters": tool["input_schema"]}
            for tool in tools
        ]
        started = perf_counter()
        response = self._client().responses.create(
            model=settings.openai_model,
            instructions="필요한 경우에만 여행 조회 Tool 하나를 선택하세요.",
            input=message,
            tools=openai_tools,
            tool_choice=tool_choice,
        )
        call = next((item for item in response.output if item.type == "function_call"), None)
        arguments = json.loads(call.arguments) if call else {}
        return ProviderToolCall(self.name, settings.openai_model, call.name if call else None, arguments, "OpenAI Tool Calling 결과", 0.9 if call else 0.4, round((perf_counter() - started) * 1000), {"name": call.name, "arguments": call.arguments} if call else None)

    def status(self) -> dict[str, Any]:
        return {"provider": self.name, "configured": bool(settings.openai_api_key), "model": settings.openai_model, "environment": "cloud"}
