import streamlit as st

from clients.agent_client import run_rag_agent
from core.api_client import BackendAPIError


st.title("9️⃣ RAG Agent Tool")
st.caption("Agent가 search_knowledge_base Tool을 실행하고 Tool Result만 근거로 답합니다.")

question = st.text_input("질문", "강아지와 호텔에 묵으면 추가 비용이 있나요?")
provider = st.selectbox("Provider", ["mock", "ollama", "openai", "gemini"])
mode = st.selectbox("Tool 검색 방식", ["hybrid", "pgvector", "keyword"])

if st.button("Agent 실행", type="primary"):
    try:
        result = run_rag_agent(question, provider, mode)
        st.subheader("Tool Call")
        st.json(result["tool_call"])
        st.subheader("Tool Result")
        st.json(result["tool_result"])
        st.subheader("최종 답변")
        st.write(result["final_answer"])
        st.caption(f"출처: {', '.join(result['sources']) or '없음'}")
    except BackendAPIError as error:
        st.error(str(error))
