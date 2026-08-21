"""TOOLS 도메인의 Pydantic API 계약입니다."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import TextRequest


class ToolSelectRequest(TextRequest):
    pass


class ToolRunRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class WeatherArgs(BaseModel):
    city: str = Field(min_length=1)
    target_date: date


class HotelArgs(BaseModel):
    city: str = Field(min_length=1)
    check_in: date
    check_out: date
    guests: int = Field(ge=1, le=10)

    @model_validator(mode="after")
    def validate_dates(self) -> "HotelArgs":
        if self.check_out <= self.check_in:
            raise ValueError("체크아웃은 체크인 이후여야 합니다.")
        return self


class AttractionArgs(BaseModel):
    city: str = Field(min_length=1)
    category: Literal["nature", "culture", "food", "all"] = "all"

