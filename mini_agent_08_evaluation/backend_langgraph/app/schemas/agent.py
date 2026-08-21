"""AGENT 도메인의 Pydantic API 계약입니다."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import TextRequest


class AgentRunRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)
    destination: str | None = None
    start_date: date | None = None
    nights: int | None = Field(default=None, ge=1, le=30)
    adults: int | None = Field(default=None, ge=1, le=20)
    budget: int | None = Field(default=None, gt=0)


class AgentDecisionRequest(BaseModel):
    actor: str = Field(default="demo-user", min_length=1, max_length=100)
    note: str = Field(default="", max_length=500)

