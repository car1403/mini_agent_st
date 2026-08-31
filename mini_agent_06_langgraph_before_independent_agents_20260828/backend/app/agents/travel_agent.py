from typing import Any

from app.graphs.state import AgentState
from app.providers.openai import continue_response, create_client, create_response


async def agent_node(state: AgentState) -> dict[str, Any]:
    """AI Agent 영역: OpenAI Model이 다음 MCP Tool 또는 종료를 판단합니다."""
    trace = list(state.get("trace", []))
    try:
        client = create_client()
        previous_id = state.get("previous_response_id")
        if previous_id:
            response = await continue_response(
                client,
                previous_id,
                state.get("tool_outputs", []),
                state["openai_tools"],
            )
        else:
            response = await create_response(client, state["question"], state["openai_tools"])
    except Exception as error:
        trace.append({"owner": "workflow", "stage": "model_error", "error": str(error)})
        return {"status": "failed", "termination_reason": "model_error", "pending_calls": [], "trace": trace}

    calls = [item for item in response.output if item.type == "function_call"]
    llm_calls = state.get("llm_calls", 0) + 1
    if calls:
        trace.append({"owner": "ai_agent", "stage": "model_selected_mcp_tools", "tools": [call.name for call in calls]})
        return {
            "previous_response_id": response.id,
            "pending_calls": calls,
            "tool_outputs": [],
            "llm_calls": llm_calls,
            "status": "running",
            "trace": trace,
        }

    trace.append({"owner": "ai_agent", "stage": "model_final_answer", "text": response.output_text})
    return {
        "previous_response_id": response.id,
        "pending_calls": [],
        "answer": response.output_text,
        "llm_calls": llm_calls,
        "status": "completed",
        "termination_reason": "model_finished",
        "trace": trace,
    }
