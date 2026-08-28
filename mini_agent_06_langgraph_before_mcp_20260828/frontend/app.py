import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Mini Agent 06 · LangGraph AI Agent", page_icon="🔁", layout="wide")
st.title("Mini Agent 06 · LangGraph AI Agent")
st.caption("AI Agent가 다음 행동을 판단하고, Workflow가 실행을 통제하며, LangGraph가 State와 이동을 관리합니다.")

with st.expander("세 영역의 책임 보기"):
    st.markdown(
        """
| 영역 | 이 프로젝트에서 하는 일 |
| --- | --- |
| AI Agent | OpenAI Model이 다음 Tool 또는 최종 답변을 선택 |
| Workflow | Tool Allowlist·arguments 검증, 실행과 오류 기록 |
| LangGraph | State, Agent Node, Tool Node, 반복·분기·종료 관리 |

AI Agent만으로도 Python Loop를 만들 수 있고, Model이 작업 순서를 계획할 수도 있습니다.
여기서는 판단과 결정적 통제를 분리하고, 그 실행 구조를 LangGraph로 명시적으로 표현합니다.
"""
    )

question = st.text_area("질문", "제주 날씨에 맞는 장소를 추천해 줘.", height=100)

if st.button("AI Agent 실행", type="primary", use_container_width=True):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/agent/run",
            json={"question": question},
            timeout=90,
        )
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
        col4.metric("Tool 호출", result["tool_calls"])

        st.subheader("Agent Trace")
        for index, item in enumerate(result["trace"], start=1):
            owner = item.get("owner", "system")
            stage = item.get("stage", "unknown")
            with st.expander(f"{index}. {owner} · {stage}", expanded=True):
                st.json(item)

st.divider()
st.code("START → AI Agent Node → Tool Call? → Workflow Tool Node → AI Agent Node → END", language="text")
