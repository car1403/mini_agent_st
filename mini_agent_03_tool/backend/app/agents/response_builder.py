"""Tool 실행 결과를 사용자의 최종 자연어 답변으로 변환합니다.

`agents.tool_loop.run_tool_agent()`가 Tool 실행 성공 후 호출합니다.
"""

import json

from app.schemas.stage_03 import ToolRunResult
from app.services.generation_service import generate


def build_final_answer(provider: str, question: str, tool_result: ToolRunResult) -> str:
    if provider == "mock":
        return f"{tool_result.tool_name} 조회 결과입니다: {json.dumps(tool_result.data, ensure_ascii=False)}"
    prompt = f"사용자 질문: {question}\nTool 이름: {tool_result.tool_name}\nTool Result: {json.dumps(tool_result.data, ensure_ascii=False)}"
    try:
        return str(generate(provider, "Tool Result에 있는 값만 사용해 친절한 한국어 최종 답변을 작성하세요.", prompt).content)
    except Exception as error:
        return f"Tool 실행은 성공했지만 최종 답변 생성에 실패했습니다: {error}"
