import os

import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8008")

st.set_page_config(page_title="Mini Agent 08", page_icon="🧪", layout="wide")
st.title("🧪 Safe Order Agent 평가")
st.caption("Scenario → Check → Trace → Regression")
st.info(
    "07에서 만든 Safe Order Agent의 저장된 실행 결과를 6개 안전 Scenario로 검사합니다. "
    "실제 주문이나 OpenAI API는 호출하지 않습니다."
)

inject_regression = st.checkbox(
    "학습용 회귀 오류 넣기",
    help="정상 주문이 승인 대기를 건너뛰고 place_order를 실행한 결과로 바꿉니다.",
)

if st.button("전체 평가 실행", type="primary", use_container_width=True):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/evaluations/run",
            json={"inject_regression": inject_regression},
            timeout=10,
        )
        response.raise_for_status()
        st.session_state["report"] = response.json()
    except requests.RequestException as error:
        st.error(f"Backend에 연결할 수 없습니다: {error}")

report = st.session_state.get("report")
if report:
    total, passed, failed, gate = st.columns(4)
    total.metric("전체 Scenario", report["total"])
    passed.metric("통과", report["passed"])
    failed.metric("실패", report["failed"])
    gate.metric("Safety Gate", report["safety_gate"])

    if report["safety_gate"] == "PASS":
        st.success("모든 안전 조건을 통과했습니다.")
    else:
        st.error("Safety Critical Scenario가 실패했습니다. 배포하면 안 됩니다.")

    st.subheader("Scenario 결과")
    for result in report["results"]:
        icon = "✅" if result["passed"] else "❌"
        with st.expander(f"{icon} {result['description']}", expanded=not result["passed"]):
            left, right = st.columns(2)
            left.write(f"기대 상태: `{result['expected_status']}`")
            right.write(f"실제 상태: `{result['actual_status']}`")
            st.write("실행 Tool:", result["executed_tools"] or "없음")
            st.write("검사 결과:", result["checks"])
            if result["failed_checks"]:
                st.warning("실패한 검사: " + ", ".join(result["failed_checks"]))
            st.markdown("**Trace**")
            st.json(result["trace"])
else:
    st.write("`전체 평가 실행`을 눌러 6개 Scenario를 확인하세요.")

st.divider()
with st.expander("선택 · 실행 중인 Mini Agent 07 평가"):
    st.caption("07의 OpenAI Agent와 HTTP MCP Server가 실행 중일 때 정상 주문 요청 한 건을 평가합니다.")
    live_url = st.text_input("Mini Agent 07 Backend", "http://127.0.0.1:8000")
    if st.button("07 실제 실행 결과 평가"):
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/evaluations/live",
                json={"api_base_url": live_url},
                timeout=100,
            )
            response.raise_for_status()
            live = response.json()["result"]
            if live["passed"]:
                st.success("실제 07 Agent가 정상 주문 승인 대기 Scenario를 통과했습니다.")
            else:
                st.error("실제 07 Agent 결과가 기대 행동과 다릅니다.")
            st.json(live)
        except requests.RequestException as error:
            st.error(f"Live 평가 실패: {error}")
