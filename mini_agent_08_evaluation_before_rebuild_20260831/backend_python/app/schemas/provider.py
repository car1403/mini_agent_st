"""PROVIDER 도메인의 Pydantic API 계약입니다."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import TextRequest


class ProviderGenerateRequest(TextRequest):
    provider: Literal["mock", "openai", "gemini", "ollama"] | None = None
    system_prompt: str = Field(
        default="당신은 초보자를 돕는 친절한 여행 상담 도우미입니다.",
        max_length=2000,
    )


class TravelPlan(BaseModel):
    destination: str
    summary: str
    recommended_days: int = Field(ge=1, le=30)
    activities: list[str] = Field(min_length=1, max_length=10)
    cautions: list[str] = Field(default_factory=list, max_length=10)


class TravelExtractRequest(TextRequest):
    reference_date: date = date(2026, 7, 27)

