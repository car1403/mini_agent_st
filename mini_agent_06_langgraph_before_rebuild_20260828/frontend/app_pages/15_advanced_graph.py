import streamlit as st

from clients.learning_client import run_advanced_graph, run_llm_node, stream_graph
from core.api_client import BackendAPIError


st.title("🧩 실제 Agent Graph")
st.caption("Streaming, LLM, Tool, RAG, Memory Node와 State Trace를 확인합니다.")

message = st.text_input("질문", "부산 날씨를 알려줘")
provider = st.selectbox("LLM Provider", ["mock", "gemini", "openai", "ollama"])

left, middle, right = st.columns(3)
with left:
    if st.button("Node Streaming"):
        try:
            st.json(stream_graph(message))
        except BackendAPIError as error:
            st.error(str(error))
with middle:
    if st.button("LLM Node"):
        try:
            st.json(run_llm_node(message, provider))
        except BackendAPIError as error:
            st.error(str(error))
with right:
    if st.button("전체 Graph", type="primary"):
        try:
            result = run_advanced_graph("demo-user", message, provider)
            st.success(result["answer"])
            st.json(result)
        except BackendAPIError as error:
            st.error(str(error))
