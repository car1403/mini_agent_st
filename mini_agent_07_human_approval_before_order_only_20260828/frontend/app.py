import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Mini Agent 07 · Human Approval", page_icon="🛡️", layout="wide")
st.title("Mini Agent 07 · Human Approval and Safety")
st.caption("읽기 Tool은 자동 실행하고 외부 상태를 바꾸는 Tool은 승인 Snapshot을 확인한 뒤 실행합니다.")


def get(path: str):
    response = requests.get(f"{API_BASE_URL}{path}", timeout=5)
    response.raise_for_status()
    return response.json()


def post(path: str, payload: dict):
    response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=90)
    response.raise_for_status()
    return response.json()


try:
    agents = get("/api/agents")
except requests.RequestException as error:
    st.error(f"Backend 연결 실패: {error}")
    st.stop()

try:
    mcp = get("/api/agents/mcp-status")
except requests.RequestException:
    st.warning("MCP Tool Server에 연결할 수 없습니다. 8010 포트의 Server를 먼저 실행하세요.")
else:
    st.success(f"MCP 연결: {mcp['status']} · Tool {mcp['tool_count']}개")

labels = {agent["agent_id"]: f"{agent['name']} · {agent['goal']}" for agent in agents}
agent_id = st.selectbox("실행할 Single Agent", options=list(labels), format_func=labels.get)
selected = next(agent for agent in agents if agent["agent_id"] == agent_id)

with st.expander("선택한 Agent의 안전 경계", expanded=True):
    st.markdown(f"**Goal**  \n{selected['goal']}")
    st.markdown("**허용된 Tool**")
    st.code("\n".join(selected["allowed_tools"]), language="text")
    st.caption("허용 목록 안의 Tool이라도 변경 Tool은 사용자 승인 전에는 실행되지 않습니다.")

actor_id = st.text_input("현재 사용자 ID", "user-01")
question_key = f"question_{agent_id}"
if question_key not in st.session_state:
    st.session_state[question_key] = selected["example_question"]
question = st.text_area("질문", key=question_key, height=100)

if "run_result" not in st.session_state:
    st.session_state.run_result = None

if st.button("안전 Agent 실행", type="primary", use_container_width=True):
    try:
        st.session_state.run_result = post(
            "/api/agents/runs",
            {"agent_id": agent_id, "actor_id": actor_id, "question": question},
        )
    except requests.RequestException as error:
        st.error(f"Agent 실행 실패: {error}")

result = st.session_state.run_result
if result:
    if result["status"] == "waiting_approval":
        pending = result["pending_approval"]
        st.warning(pending["question"])
        st.markdown("### 승인 대상 Snapshot")
        st.json(pending["approval_target"])
        note = st.text_input("승인·거절 메모", key=f"note_{result['run_id']}")
        approve_col, reject_col = st.columns(2)

        def decide(decision: str):
            return post(
                f"/api/agents/runs/{result['run_id']}/decision",
                {
                    "actor_id": actor_id,
                    "decision": decision,
                    "approval_target": pending["approval_target"],
                    "note": note,
                },
            )

        if approve_col.button("승인 후 변경 실행", type="primary", use_container_width=True):
            try:
                st.session_state.run_result = decide("approve")
                st.rerun()
            except requests.RequestException as error:
                st.error(f"승인 처리 실패: {error}")
        if reject_col.button("거절", use_container_width=True):
            try:
                st.session_state.run_result = decide("reject")
                st.rerun()
            except requests.RequestException as error:
                st.error(f"거절 처리 실패: {error}")
    elif result["status"] == "completed":
        st.success(result.get("answer") or "승인된 작업이 완료되었습니다.")
    elif result["status"] == "rejected":
        st.info("사용자가 변경 작업을 거절했습니다.")
    else:
        st.error(f"실행 종료: {result['termination_reason']}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("상태", result["status"])
    col2.metric("종료 이유", result["termination_reason"])
    col3.metric("LLM 호출", result["llm_calls"])
    col4.metric("MCP Tool 호출", result["tool_calls"])

    st.subheader("Agent·Policy·Approval Trace")
    for index, item in enumerate(result["trace"], start=1):
        with st.expander(f"{index}. {item.get('owner', 'system')} · {item.get('stage', 'unknown')}"):
            st.json(item)

    try:
        audit = get(f"/api/agents/runs/{result['run_id']}/audit")
    except requests.RequestException:
        pass
    else:
        with st.expander("Audit Log"):
            st.json(audit)

st.divider()
st.info("다음 Multi-Agent 과정에서도 Coordinator와 다른 Agent의 요청은 같은 Backend Policy와 승인 경계를 통과해야 합니다.")
