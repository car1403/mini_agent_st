"""실제 LLM·Tool·RAG·Memory를 연결하는 확장 LangGraph 학습 예제입니다."""

from operator import add
from time import perf_counter
from typing import Annotated, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.providers.registry import run_with_optional_fallback
from app.rag.policies import search as search_policies
from app.repositories.store import store
from app.agents.mock_selector import select_tool
from app.tools.executor import run_tool


class AdvancedState(TypedDict, total=False):
    user_id: str
    message: str
    provider: str
    route: str
    memories: list[dict]
    documents: list[dict]
    tool_call: dict
    tool_result: dict
    answer: str
    status: str
    trace: Annotated[list[dict], add]


def _event(node: str, started: float, **data) -> dict:
    return {"node": node, "latency_ms": round((perf_counter() - started) * 1000), **data}


def load_context(state: AdvancedState) -> dict:
    started = perf_counter()
    memories = store.list_memories(state["user_id"])
    documents = search_policies(state["message"], 2)
    return {
        "memories": memories,
        "documents": documents,
        "trace": [_event("load_context", started, memories=len(memories), documents=len(documents))],
    }


def decide_action(state: AdvancedState) -> dict:
    started = perf_counter()
    decision = select_tool(state["message"])
    route = "tool" if decision.get("tool_name") else "answer"
    return {"route": route, "tool_call": decision, "trace": [_event("decide_action", started, route=route)]}


def route_action(state: AdvancedState) -> Literal["run_tool", "generate_answer"]:
    return "run_tool" if state["route"] == "tool" else "generate_answer"


def execute_tool(state: AdvancedState) -> dict:
    started = perf_counter()
    call = state["tool_call"]
    # 수업용 기본 인자는 Backend Allowlist의 조회 Tool에만 전달합니다.
    arguments = {"city": "부산", "target_date": "2026-08-19"}
    if call["tool_name"] == "search_hotels":
        arguments = {"city": "부산", "check_in": "2026-08-20", "check_out": "2026-08-22", "guests": 2}
    elif call["tool_name"] == "search_attractions":
        arguments = {"city": "부산", "category": "all"}
    result = run_tool(call["tool_name"], arguments)
    return {"tool_result": result, "trace": [_event("run_tool", started, tool_name=call["tool_name"])]}


def generate_answer(state: AdvancedState) -> dict:
    started = perf_counter()
    context = {
        "memories": state.get("memories", []),
        "documents": state.get("documents", []),
        "tool_result": state.get("tool_result"),
    }
    result = run_with_optional_fallback(
        lambda provider: provider.generate(
            "제공된 Context만 사용해 한국어로 답하세요. 없는 정보는 추측하지 마세요.",
            f"질문: {state['message']}\nContext: {context}",
        ),
        state.get("provider"),
    )
    data = result.to_dict()
    return {
        "answer": str(data["content"]),
        "status": "completed",
        "trace": [_event("generate_answer", started, provider=data["provider"], model=data["model"])],
    }


builder = StateGraph(AdvancedState)
builder.add_node("load_context", load_context)
builder.add_node("decide_action", decide_action)
builder.add_node("run_tool", execute_tool)
builder.add_node("generate_answer", generate_answer)
builder.add_edge(START, "load_context")
builder.add_edge("load_context", "decide_action")
builder.add_conditional_edges("decide_action", route_action)
builder.add_edge("run_tool", "generate_answer")
builder.add_edge("generate_answer", END)
advanced_graph = builder.compile()


def stream_graph(message: str) -> dict:
    events = []
    for update in advanced_graph.stream(
        {"user_id": "demo-user", "message": message, "provider": "mock", "trace": []},
        stream_mode="updates",
    ):
        node, values = next(iter(update.items()))
        events.append({"node": node, "update": values})
    return {"message": message, "events": events}


def run_llm_node(message: str, provider: str) -> dict:
    started = perf_counter()
    result = run_with_optional_fallback(
        lambda selected: selected.generate("한 문장으로 친절하게 답하세요.", message), provider,
    ).to_dict()
    return {**result, "trace": [_event("llm_node", started, provider=result["provider"])]}


def run_advanced_graph(user_id: str, message: str, provider: str) -> dict:
    return advanced_graph.invoke({"user_id": user_id, "message": message, "provider": provider, "trace": []})
