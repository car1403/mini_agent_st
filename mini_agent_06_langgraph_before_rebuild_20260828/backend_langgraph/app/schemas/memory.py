"""MEMORY 도메인의 Pydantic API 계약입니다."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import TextRequest


class MemoryCreateRequest(BaseModel):
    key: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=500)

