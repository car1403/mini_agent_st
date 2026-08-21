"""Provider 공통 Protocol과 호출 시간 측정 기능을 정의합니다."""

from time import perf_counter
from typing import Any, Callable, Protocol, TypeVar

from pydantic import BaseModel
from app.providers.models import ProviderResult


T = TypeVar("T", bound=BaseModel)


class LlmProvider(Protocol):
    name: str
    model: str

    def generate(self, system_prompt: str, message: str) -> ProviderResult: ...

    def generate_structured(
        self,
        system_prompt: str,
        message: str,
        response_model: type[T],
    ) -> ProviderResult: ...


def timed_call(call: Callable[[], Any]) -> tuple[Any, int]:
    started = perf_counter()
    value = call()
    return value, round((perf_counter() - started) * 1000)
