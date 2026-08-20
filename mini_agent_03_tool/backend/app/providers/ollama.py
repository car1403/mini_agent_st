"""Ollama HTTP API를 공통 Provider 계약으로 변환하는 어댑터입니다.

`providers.registry`가 생성하며 generation/structured services와 `agents.tool_selector`가 사용합니다.
"""

from time import perf_counter
from typing import Any

from pydantic import BaseModel

from app.core.config import settings
from app.providers.models import ProviderResult, ProviderToolCall


class OllamaProvider:
    name = "ollama"

    def _chat(self, system_prompt: str, message: str, format_: dict | None = None, tools: list[dict] | None = None) -> dict:
        import httpx

        payload: dict[str, Any] = {"model": settings.ollama_model, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}], "stream": False}
        if format_ is not None:
            payload["format"] = format_
        if tools is not None:
            payload["tools"] = tools
        response = httpx.post(f"{settings.ollama_base_url}/api/chat", json=payload, timeout=settings.request_timeout_seconds)
        response.raise_for_status()
        return response.json()

    def generate(self, system_prompt: str, message: str) -> ProviderResult:
        started = perf_counter()
        body = self._chat(system_prompt, message)
        return ProviderResult(self.name, settings.ollama_model, body["message"]["content"], round((perf_counter() - started) * 1000))

    def generate_structured(self, system_prompt: str, message: str, response_schema: type[BaseModel]) -> ProviderResult:
        started = perf_counter()
        body = self._chat(system_prompt, message, response_schema.model_json_schema())
        parsed = response_schema.model_validate_json(body["message"]["content"])
        return ProviderResult(self.name, settings.ollama_model, parsed.model_dump(), round((perf_counter() - started) * 1000))

    def select_tool(self, message: str, tools: list[dict[str, Any]], tool_choice: str = "auto") -> ProviderToolCall:
        ollama_tools = [{"type": "function", "function": {"name": tool["name"], "description": tool["description"], "parameters": tool["input_schema"]}} for tool in tools]
        instruction = "반드시 여행 조회 Tool 하나를 선택하세요." if tool_choice == "required" else "필요한 경우에만 여행 조회 Tool 하나를 선택하세요."
        started = perf_counter()
        body = self._chat(instruction, message, tools=ollama_tools)
        calls = body.get("message", {}).get("tool_calls", [])
        call = calls[0].get("function", {}) if calls else {}
        arguments = call.get("arguments", {})
        return ProviderToolCall(self.name, settings.ollama_model, call.get("name"), arguments, "Ollama Tool Calling 결과", 0.85 if call else 0.4, round((perf_counter() - started) * 1000), call or None)

    def status(self) -> dict[str, Any]:
        return {"provider": self.name, "configured": True, "model": settings.ollama_model, "base_url": settings.ollama_base_url, "environment": "local-docker"}
