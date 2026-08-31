"""EVALUATION 도메인의 Pydantic API 계약입니다."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import TextRequest


class EvaluationScenario(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)
    expected_tool: str | None = Field(default=None, max_length=100)
    expected_status: Literal["completed", "needs_input", "blocked"]


class EvaluationRunRequest(BaseModel):
    scenarios: list[EvaluationScenario] = Field(default_factory=list, max_length=50)

