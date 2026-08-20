"""Tool 선택·검증·한 번의 실행·최종 답변으로 이루어진 단일 Agent Cycle을 조정합니다.

`routers.stage_03_router`의 `/api/tools/complete` Endpoint에서 사용하며 반복 Agent의 기초가 됩니다.
"""

from app.agents.response_builder import build_final_answer
from app.agents.tool_selector import decide_tool
from app.schemas.stage_03 import ToolCompleteResult, ToolSelectionResult
from app.tools.executor import execute_tool_safely


def run_tool_agent(provider: str, message: str, tool_choice: str = "auto") -> ToolCompleteResult:
    raw_decision = decide_tool(provider, message, tool_choice)
    decision = ToolSelectionResult.model_validate(raw_decision.__dict__)
    trace = [{"stage": "tool_selection", "data": decision.model_dump(mode="json")}]
    if decision.needs_clarification:
        trace.append({"stage": "clarification", "data": {"missing_arguments": decision.missing_arguments, "follow_up_question": decision.follow_up_question}})
        return ToolCompleteResult(provider=provider, question=message, decision=decision, final_answer=decision.follow_up_question, trace=trace)
    if decision.tool_name is None:
        trace.append({"stage": "finish", "data": {"reason": "no_tool"}})
        return ToolCompleteResult(provider=provider, question=message, decision=decision, final_answer="이 질문에는 실행할 조회 Tool이 필요하지 않습니다.", trace=trace)
    tool_result = execute_tool_safely(decision.tool_name, decision.arguments)
    trace.append({"stage": "tool_result", "data": tool_result.model_dump(mode="json")})
    if not tool_result.success:
        return ToolCompleteResult(provider=provider, question=message, decision=decision, tool_result=tool_result, final_answer="Tool을 안전하게 실행하지 못했습니다. 입력과 권한을 확인해 주세요.", trace=trace)
    final_answer = build_final_answer(provider, message, tool_result)
    return ToolCompleteResult(provider=provider, question=message, decision=decision, tool_result=tool_result, final_answer=final_answer, trace=trace + [{"stage": "final_answer", "data": {"text": final_answer}}])
