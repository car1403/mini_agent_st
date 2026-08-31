"""Provider 구현 선택·상태 조회·Fallback 실행을 관리하는 레지스트리입니다.

Router와 Workflow는 구체 Provider 대신 이 모듈의 공통 진입점을 사용합니다.
"""

from app.core.config import settings
from app.providers.mock import MockProvider


SUPPORTED_PROVIDERS = ("mock", "openai", "gemini", "ollama")


def get_provider(name: str | None = None):
    selected = (name or settings.llm_provider).lower()
    if selected == "mock":
        return MockProvider()
    if selected == "openai":
        from app.providers.openai import OpenAIProvider

        return OpenAIProvider(settings.openai_api_key, settings.openai_model)
    if selected == "gemini":
        from app.providers.gemini import GeminiProvider

        return GeminiProvider(settings.gemini_api_key, settings.gemini_model)
    if selected == "ollama":
        from app.providers.ollama import OllamaProvider

        return OllamaProvider(
            settings.ollama_base_url,
            settings.ollama_model,
            settings.request_timeout_seconds,
        )
    raise ValueError(
        f"지원하지 않는 Provider입니다: {selected}. "
        f"선택 가능: {', '.join(SUPPORTED_PROVIDERS)}"
    )


def provider_status() -> list[dict]:
    return [
        {"provider": "mock", "configured": True, "model": "deterministic-travel-mock"},
        {
            "provider": "openai",
            "configured": bool(settings.openai_api_key),
            "model": settings.openai_model,
        },
        {
            "provider": "gemini",
            "configured": bool(settings.gemini_api_key and settings.gemini_model),
            "model": settings.gemini_model or "(GEMINI_MODEL 미설정)",
        },
        {
            "provider": "ollama",
            "configured": True,
            "model": settings.ollama_model,
            "base_url": settings.ollama_base_url,
        },
    ]


def run_with_optional_fallback(operation, provider_name: str | None = None):
    primary = get_provider(provider_name)
    try:
        return operation(primary)
    except Exception:
        if not settings.llm_fallback_enabled:
            raise
        fallback = get_provider(settings.llm_fallback_provider)
        if fallback.name == primary.name:
            raise
        result = operation(fallback)
        result.fallback_used = True
        return result
