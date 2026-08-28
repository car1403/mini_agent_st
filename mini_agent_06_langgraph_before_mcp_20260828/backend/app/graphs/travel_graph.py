from typing import Any

from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph

from app.agents.travel_agent import agent_node
from app.core.config import MAX_AGENT_STEPS, OPENAI_MODEL
from app.graphs.state import AgentState
from app.tools.registry import execute_call


def tool_node(state: AgentState) -> dict[str, Any]:
    """Workflow 영역: Model 제안을 검증하고 허용된 Tool만 실행합니다."""
    outputs = []
    trace = list(state.get("trace", []))
    try:
        for call in state.get("pending_calls", []):
            output, item = execute_call(call)
            outputs.append(output)
            trace.append({"owner": "workflow", "stage": "tool_executed", **item})
    except (AttributeError, TypeError, ValueError) as error:
        trace.append({"owner": "workflow", "stage": "invalid_tool_call", "error": str(error)})
        return {"status": "failed", "termination_reason": "invalid_tool_call", "pending_calls": [], "trace": trace}
    except Exception as error:
        trace.append({"owner": "workflow", "stage": "tool_error", "error": str(error)})
        return {"status": "failed", "termination_reason": "tool_error", "pending_calls": [], "trace": trace}
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
    builder.add_node("workflow_tools", tool_node)
    builder.add_edge(START, "ai_agent")
    builder.add_conditional_edges("ai_agent", route_after_agent, {"tools": "workflow_tools", "finish": END})
    builder.add_conditional_edges("workflow_tools", route_after_tools, {"agent": "ai_agent", "finish": END})
    return builder.compile()


def run_graph(question: str) -> dict[str, Any]:
    initial: AgentState = {
        "question": question,
        "status": "running",
        "termination_reason": None,
        "llm_calls": 0,
        "tool_calls": 0,
        "trace": [{"owner": "langgraph", "stage": "graph_started"}],
    }
    try:
        result = build_graph().invoke(initial, config={"recursion_limit": MAX_AGENT_STEPS * 2 + 1})
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
