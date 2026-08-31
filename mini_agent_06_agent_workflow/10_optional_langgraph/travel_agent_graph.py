"""메인 Travel Agent와 같은 Profile·MCP Tool을 LangGraph로 실행합니다."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.agents.travel_agent import TRAVEL_AGENT  # noqa: E402
from app.core.config import MAX_AGENT_STEPS  # noqa: E402
from app.mcp.client import call_tool, discover_tools  # noqa: E402
from app.providers.openai import create_client, first_response, next_response  # noqa: E402


class State(TypedDict, total=False):
    question: str
    tools: list[dict[str, Any]]
    response_id: str
    pending_calls: list[Any]
    outputs: list[dict[str, Any]]
    answer: str
    trace: list[dict[str, Any]]


async def agent_node(state: State) -> dict[str, Any]:
    client = create_client()
    if state.get("response_id"):
        response = await next_response(
            client,
            state["response_id"],
            state.get("outputs", []),
            TRAVEL_AGENT.instructions,
            state["tools"],
        )
    else:
        response = await first_response(client, state["question"], TRAVEL_AGENT.instructions, state["tools"])
    calls = [item for item in response.output if item.type == "function_call"]
    trace = list(state.get("trace", []))
    if calls:
        trace.append({"node": "agent", "tools": [call.name for call in calls]})
        return {"response_id": response.id, "pending_calls": calls, "outputs": [], "trace": trace}
    trace.append({"node": "agent", "answer": response.output_text})
    return {"response_id": response.id, "pending_calls": [], "answer": response.output_text, "trace": trace}


async def tool_node(state: State) -> dict[str, Any]:
    outputs = []
    trace = list(state.get("trace", []))
    for call in state.get("pending_calls", []):
        arguments = json.loads(call.arguments)
        result, item = await call_tool(call.name, arguments, TRAVEL_AGENT.allowed_tools)
        outputs.append(
            {"type": "function_call_output", "call_id": call.call_id, "output": json.dumps(result, ensure_ascii=False)}
        )
        trace.append({"node": "mcp_tool", **item})
    return {"pending_calls": [], "outputs": outputs, "trace": trace}


def route(state: State) -> str:
    return "tools" if state.get("pending_calls") else "finish"


def build_graph():
    builder = StateGraph(State)
    builder.add_node("agent", agent_node)
    builder.add_node("mcp_tools", tool_node)
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", route, {"tools": "mcp_tools", "finish": END})
    builder.add_edge("mcp_tools", "agent")
    return builder.compile()


async def main() -> None:
    tools = await discover_tools(TRAVEL_AGENT.allowed_tools)
    result = await build_graph().ainvoke(
        {"question": TRAVEL_AGENT.example_question, "tools": tools, "trace": []},
        config={"recursion_limit": MAX_AGENT_STEPS * 2 + 1},
    )
    print(json.dumps({"answer": result.get("answer"), "trace": result["trace"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
