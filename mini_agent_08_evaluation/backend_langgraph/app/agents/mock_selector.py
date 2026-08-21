"""외부 LLM 없이 질문에서 교육용 여행 Tool을 선택합니다."""

def select_tool(message:str)->dict:
    if any(word in message for word in ("날씨","기온","우산","비가 와")): return {"tool_name":"get_weather","reason":"날씨 관련 요청","confidence":0.92}
    if any(word in message for word in ("호텔","숙소","체크인")): return {"tool_name":"search_hotels","reason":"숙소 관련 요청","confidence":0.94}
    if any(word in message for word in ("관광지","가볼","명소")): return {"tool_name":"search_attractions","reason":"관광지 관련 요청","confidence":0.9}
    return {"tool_name":None,"reason":"필요한 Tool을 확정할 수 없음","confidence":0.35}
