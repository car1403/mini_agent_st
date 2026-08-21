"""실행 가능한 Tool을 이름·입력 모델·함수의 단일 명세로 등록합니다."""

from collections.abc import Callable
from dataclasses import dataclass
from pydantic import BaseModel
from app.schemas import AttractionArgs,HotelArgs,WeatherArgs
from app.tools.travel import get_weather,search_attractions,search_hotels

@dataclass(frozen=True)
class ToolSpec:
    name:str
    input_model:type[BaseModel]
    function:Callable[[dict],dict]
    def execute(self,arguments:dict)->dict:
        self.input_model.model_validate(arguments);return self.function(arguments)

TOOL_REGISTRY={"get_weather":ToolSpec("get_weather",WeatherArgs,get_weather),"search_hotels":ToolSpec("search_hotels",HotelArgs,search_hotels),"search_attractions":ToolSpec("search_attractions",AttractionArgs,search_attractions)}
