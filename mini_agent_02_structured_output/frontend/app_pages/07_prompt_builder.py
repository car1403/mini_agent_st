import streamlit as st

from clients.agent_client import preview_prompt
from core.api_client import BackendAPIError


st.title("🧩 Prompt 구성")
st.caption("도메인이 달라도 역할, 지시, 맥락, 제약을 같은 방식으로 나눌 수 있습니다.")
examples = {
    "여행 요청 분석": (
        "당신은 초보자를 돕는 여행 요청 분석가입니다.",
        "사용자의 여행 요청에서 필요한 정보를 추출하세요.",
        "사용자는 국내 여행을 계획하고 있습니다.",
        "추측하지 말고 모르는 값은 누락 정보로 표시하세요.",
    ),
    "고객 문의 분류": (
        "당신은 온라인 쇼핑몰 고객 지원 분류 담당자입니다.",
        "문의를 유형과 긴급도로 분류하고 핵심 내용을 요약하세요.",
        "분류 결과는 담당 팀을 자동 배정하는 데 사용됩니다.",
        "긴급도 판단 근거를 한 문장으로 작성하세요.",
    ),
    "회의 내용 요약": (
        "당신은 프로젝트 회의 기록 정리자입니다.",
        "결정 사항과 담당자별 할 일을 구분해 정리하세요.",
        "개발자, 디자이너, 운영 담당자가 참여한 회의입니다.",
        "확정되지 않은 내용은 결정 사항에 포함하지 마세요.",
    ),
}
selected = st.selectbox("Prompt 예제", list(examples))
defaults = examples[selected]
role = st.text_input("Role", defaults[0], key=f"role-{selected}")
instruction = st.text_area("Instruction", defaults[1], key=f"instruction-{selected}")
context = st.text_area("Context", defaults[2], key=f"context-{selected}")
constraint = st.text_area("Constraint", defaults[3], key=f"constraint-{selected}")

if st.button("Prompt 조립"):
    try:
        result = preview_prompt(role, instruction, context, constraint)
        st.code(result["prompt"], language="text")
    except BackendAPIError as error:
        st.error(str(error))
