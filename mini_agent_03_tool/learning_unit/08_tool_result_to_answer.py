"""Tool Result를 사용자가 읽을 수 있는 최종 답변으로 변환합니다."""

from datetime import date


def select_tool(message: str) -> dict:
    # 1단계: 질문을 보고 Tool Call만 구성합니다.
    if "날씨" in message:
        return {"tool_name": "get_weather", "arguments": {"city": "부산", "target_date": date.today().isoformat()}}
    return {"tool_name": None, "arguments": {}}


def run_tool(tool_call: dict) -> dict:
    # 2단계: Backend가 허용된 Tool인지 확인하고 결과를 만듭니다.
    if tool_call["tool_name"] != "get_weather":
        return {"success": False, "error": {"code": "TOOL_NOT_ALLOWED"}}
    return {"success": True, "data": {"city": tool_call["arguments"]["city"], "condition": "맑음", "temperature_c": 26}}


def make_final_answer(question: str, tool_result: dict) -> str:
    # 3단계: 최종 답변은 Tool Result에 실제로 존재하는 값만 사용합니다.
    if not tool_result["success"]:
        return "요청을 처리하지 못했습니다. 입력을 확인해 주세요."
    data = tool_result["data"]
    return f"{data['city']}의 교육용 날씨는 {data['condition']}, 기온은 {data['temperature_c']}도입니다."


def agent_loop(question: str) -> dict:
    # 선택 → 조건부 실행 → 최종 답변을 순서대로 연결합니다.
    tool_call = select_tool(question)
    if tool_call["tool_name"] is None:
        return {"question": question, "tool_call": tool_call, "tool_result": None, "final_answer": "이 질문에는 Tool이 필요하지 않습니다."}
    tool_result = run_tool(tool_call)
    return {"question": question, "tool_call": tool_call, "tool_result": tool_result, "final_answer": make_final_answer(question, tool_result)}


if __name__ == "__main__":
    result = agent_loop("부산 날씨를 알려줘")
    for step, value in result.items():
        print(step, "→", value)
