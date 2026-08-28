from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_graph_components_are_beginner_friendly() -> None:
    response = client.get("/api/learning/graph/components")
    assert response.status_code == 200
    assert {"state", "node", "edge", "conditional_edge", "reducer", "mermaid"} <= response.json().keys()


def test_branch_routes_by_destination() -> None:
    complete = client.post("/api/learning/graph/branch", json={"message": "부산 여행을 준비해줘"}).json()
    missing = client.post("/api/learning/graph/branch", json={"message": "여행을 준비해줘"}).json()
    assert complete["trace"] == ["extract", "create_plan"]
    assert missing["trace"] == ["extract", "ask_user"]


def test_loop_has_success_and_failure_endings() -> None:
    success = client.post("/api/learning/graph/loop", json={"budget": 400000, "max_iterations": 1}).json()
    failure = client.post("/api/learning/graph/loop", json={"budget": 200000, "max_iterations": 1}).json()
    assert success["status"] == "completed"
    assert failure["status"] == "failed"
    assert failure["trace"][-1] == "fail"


def test_checkpoint_keeps_threads_separate() -> None:
    thread_a = f"a-{uuid4()}"
    thread_b = f"b-{uuid4()}"
    first_a = client.post("/api/learning/graph/checkpoint", json={"thread_id": thread_a}).json()
    second_a = client.post("/api/learning/graph/checkpoint", json={"thread_id": thread_a}).json()
    first_b = client.post("/api/learning/graph/checkpoint", json={"thread_id": thread_b}).json()
    assert first_a["state"]["visits"] == 1
    assert second_a["state"]["visits"] == 2
    assert first_b["state"]["visits"] == 1


def test_python_and_langgraph_return_same_answer() -> None:
    result = client.post("/api/learning/graph/compare", json={"message": "제주 여행을 준비해줘"}).json()
    assert result["python"]["status"] == result["langgraph"]["status"]
    assert result["python"]["answer"] == result["langgraph"]["answer"]


def test_stream_returns_node_updates_in_order() -> None:
    result = client.post("/api/learning/graph/stream", json={"message": "부산 날씨"}).json()
    nodes = [item["node"] for item in result["events"]]
    assert nodes == ["load_context", "decide_action", "run_tool", "generate_answer"]


def test_llm_node_uses_mock_provider() -> None:
    result = client.post(
        "/api/learning/graph/llm-node",
        json={"message": "안녕하세요", "provider": "mock"},
    ).json()
    assert result["provider"] == "mock"
    assert result["trace"][0]["node"] == "llm_node"


def test_advanced_graph_routes_to_allowlisted_tool() -> None:
    result = client.post(
        "/api/learning/graph/advanced",
        json={"user_id": "demo-user", "message": "부산 날씨", "provider": "mock"},
    ).json()
    assert result["route"] == "tool"
    assert result["tool_call"]["tool_name"] == "get_weather"
    assert result["tool_result"]["source"] == "mock"
    assert result["status"] == "completed"
