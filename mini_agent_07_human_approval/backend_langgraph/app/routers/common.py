"""Router가 공통 성공 응답과 Trace ID를 만들 때 사용하는 보조 함수입니다."""

from app.schemas import ApiResponse
from app.services.travel_service import new_trace_id

def ok(data:object,trace_id:str|None=None)->ApiResponse:
    return ApiResponse(success=True,data=data,trace_id=trace_id or new_trace_id())
