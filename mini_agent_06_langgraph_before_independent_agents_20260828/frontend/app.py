import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Mini Agent 06 · Agent Workflow", page_icon="🔁", layout="wide")
st.title("Mini Agent 06 · Agent Workflow")
st.caption("OpenAI AI Agent Loop with LangGraph and HTTP MCP")

try:
    status = requests.get(f"{API_BASE_URL}/api/agent/mcp-status", timeout=5)
    status.raise_for_status()
    mcp = status.json()
except requests.RequestException:
    st.error("Travel MCP Server에 연결할 수 없습니다. 8010 포트의 MCP Server를 먼저 실행하세요.")
else:
    st.success(f"MCP 연결: {mcp['status']} · {mcp['transport']} · Tool {mcp['tool_count']}개")
    with st.expander("MCP 연결 정보"):
        st.json(mcp)

with st.expander("AI Agent, Workflow, LangGraph와 MCP의 책임"):
    st.markdown(
        """
| 영역 | 하는 일 |
| --- | --- |
| AI Agent | OpenAI Model이 다음 MCP Tool 또는 최종 답변 선택 |
| Workflow·Backend | Model 제안과 arguments 검증, 오류와 종료 기록 |
| LangGraph | State, Node, 반복·분기와 END 관리 |
| HTTP MCP Server | Backend 밖에서 실제 Tool 제공·실행 |

AI Agent만으로도 작업 순서를 계획하고 Python Loop를 구성할 수 있습니다. 이 프로젝트는 유연한 판단과 반드시 지켜야 하는 실행 규칙을 분리하고, LangGraph로 그 연결을 명시합니다.
"""
    )

question = st.text_area("질문", "제주 날씨에 맞는 장소를 추천해 줘.", height=100)

if st.button("AI Agent 실행", type="primary", use_container_width=True):
    try:
        response = requests.post(f"{API_BASE_URL}/api/agent/run", json={"question": question}, timeout=90)
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as error:
        st.error(f"Backend 호출 실패: {error}")
    else:
        if result["status"] == "completed":
            st.success(result.get("answer") or "답변이 없습니다.")
        else:
            st.error(f"실행 종료: {result['termination_reason']}")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("상태", result["status"])
        col2.metric("종료 이유", result["termination_reason"])
        col3.metric("LLM 호출", result["llm_calls"])
        col4.metric("MCP Tool 호출", result["tool_calls"])

        st.subheader("Agent Trace")
        for index, item in enumerate(result["trace"], start=1):
            with st.expander(f"{index}. {item.get('owner', 'system')} · {item.get('stage', 'unknown')}", expanded=True):
                st.json(item)

st.divider()
st.code(
    "START → AI Agent Node → HTTP MCP Tool Node → AI Agent Node → END",
    language="text",
)
