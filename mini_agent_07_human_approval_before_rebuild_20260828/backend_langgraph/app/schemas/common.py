"""COMMON 도메인의 Pydantic API 계약입니다."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[Any] = Field(default_factory=list)


class ApiResponse(BaseModel):
    success: bool
    data: Any | None = None
    error: ErrorDetail | None = None
    trace_id: str


class TextRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

