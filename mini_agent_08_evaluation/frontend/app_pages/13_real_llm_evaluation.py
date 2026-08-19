import streamlit as st

from core.ui import backend_request, run_api


st.title("8-7. 실제 LLM 응답 평가")
st.caption("문장 전체가 아니라 구조화 필드와 요청의 핵심 조건을 검사합니다.")

provider = st.selectbox("Provider", ["openai", "gemini", "ollama", "mock"])
message = st.text_area("평가 요청", "부산의 대표 장소를 포함한 2박 3일 여행 계획을 만들어 주세요.")

if st.button("LLM 호출 후 평가", type="primary"):
    result = run_api(lambda: backend_request("POST", "/api/providers/travel-plan", {"provider": provider, "message": message}))
    if result:
        plan = result.get("content", {})
        checks = {
            "구조화 출력": isinstance(plan, dict),
            "부산 포함": "부산" in str(plan.get("destination", "")),
            "여행 일수 범위": isinstance(plan.get("recommended_days"), int) and 1 <= plan["recommended_days"] <= 30,
            "활동 한 개 이상": bool(plan.get("activities")),
        }
        st.metric("평가 결과", "PASS" if all(checks.values()) else "FAIL")
        st.write({"provider": result.get("provider"), "model": result.get("model"), "latency_ms": result.get("latency_ms")})
        st.json(checks)
        st.json(plan)

st.info("실제 Provider는 API 설정과 호출 비용을 확인하세요. API Key와 전체 Prompt는 평가 결과에 저장하지 않습니다.")
