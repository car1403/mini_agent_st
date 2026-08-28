import json
from typing import Any

from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph

from app.agents.travel_agent import agent_node
from app.core.config import MAX_AGENT_STEPS, OPENAI_MODEL
from app.graphs.state import AgentState
from app.mcp.client import call_tool, discover_tools


async def mcp_tool_node(state: AgentState) -> dict[str, Any]:
    """Workflow 영역: Model 제안을 검증하고 HTTP MCP Tool을 실행합니다."""
    outputs = []
    trace = list(state.get("trace", []))
    try:
        for call in state.get("pending_calls", []):
            arguments = json.loads(call.arguments)
            if not isinstance(arguments, dict):
                raise ValueError("Tool arguments는 JSON Object여야 합니다.")
            result, item = await call_tool(call.name, arguments)
            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )
            trace.append({"owner": "mcp", "stage": "http_mcp_tool_executed", **item})
    except (AttributeError, json.JSONDecodeError, TypeError, ValueError) as error:
        trace.append({"owner": "workflow", "stage": "invalid_tool_call", "error": str(error)})
        return {"status": "failed", "termination_reason": "invalid_tool_call", "pending_calls": [], "trace": trace}
    except Exception as error:
        trace.append({"owner": "mcp", "stage": "mcp_tool_error", "error": str(error)})
        return {"status": "failed", "termination_reason": "mcp_tool_error", "pending_calls": [], "trace": trace}
    return {
        "pending_calls": [],
        "tool_outputs": outputs,
        "tool_calls": state.get("tool_calls", 0) + len(outputs),
        "trace": trace,
    }


def route_after_agent(state: AgentState) -> str:
    if state.get("status") in {"completed", "failed"}:
        return "finish"
    return "tools" if state.get("pending_calls") else "finish"


def route_after_tools(state: AgentState) -> str:
    return "finish" if state.get("status") == "failed" else "agent"


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("ai_agent", agent_node)
    builder.add_node("http_mcp_tools", mcp_tool_node)
    builder.add_edge(START, "ai_agent")
    builder.add_conditional_edges("ai_agent", route_after_agent, {"tools": "http_mcp_tools", "finish": END})
    builder.add_conditional_edges("http_mcp_tools", route_after_tools, {"agent": "ai_agent", "finish": END})
    return builder.compile()


async def run_graph(question: str) -> dict[str, Any]:
    tools = await discover_tools()
    initial: AgentState = {
        "question": question,
        "openai_tools": tools,
        "status": "running",
        "termination_reason": None,
        "llm_calls": 0,
        "tool_calls": 0,
        "trace": [
            {"owner": "langgraph", "stage": "graph_started"},
            {"owner": "mcp", "stage": "tools_discovered", "tools": [tool["name"] for tool in tools]},
        ],
    }
    try:
        result = await build_graph().ainvoke(initial, config={"recursion_limit": MAX_AGENT_STEPS * 2 + 1})
    except GraphRecursionError as error:
        initial["status"] = "stopped"
        initial["termination_reason"] = "max_steps_exceeded"
        initial["trace"].append({"owner": "langgraph", "stage": "graph_stopped", "error": str(error)})
        result = initial
    return {
        "question": question,
        "model": OPENAI_MODEL,
        "status": result.get("status", "stopped"),
        "termination_reason": result.get("termination_reason", "max_steps_exceeded"),
        "llm_calls": result.get("llm_calls", 0),
        "tool_calls": result.get("tool_calls", 0),
        "trace": result.get("trace", []),
        "answer": result.get("answer"),
    }
