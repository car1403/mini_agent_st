# 05 과정과 Mini Agent 연결표

| 05 학습 폴더 | Mini Agent 적용 위치 | 실행 결과 |
| --- | --- | --- |
| `01_llm-to-agent` | `mini_agent_01_llm` | 개념 비교·여행 분류·세 Provider 응답 |
| `02_prompt-and-structured-output` | `mini_agent_02_structured_output` | Prompt 조립·Pydantic 검증·Provider별 TravelPlan |
| `01_llm-to-agent` 확장 | `mini_agent_01_llm/learning_unit` | GPT 이미지 분석·Pydantic·TTS |
| `03_tool-use` | `mini_agent_03_tool/learning_unit` | Schema·선택·안전 실행·Agent Loop |
| `04_rag` | `mini_agent_04_rag/learning_unit` | Chunk·검색·근거 제한·Ollama Embedding·pgvector |
| `05_memory` | `mini_agent_05_memory/learning_unit` | 대화 Window·사용자 격리·개인화·Redis·PostgreSQL |
| `06_agent-workflow` | `mini_agent_06_agent_workflow` | 독립 Single Agent 3개·공통 Python Loop·Tool 권한·종료 Trace |
| `06_agent-workflow` 선택 | `mini_agent_06_agent_workflow/10_optional_langgraph` | 같은 Travel Agent의 Python Loop와 LangGraph 비교 |
| `07_human-approval-and-safety` | `mini_agent_07_human_approval` | Safe Order Agent의 주문 승인·거절·Snapshot·멱등성·Audit |
| `08_agent-evaluation-and-tracing` | `mini_agent_08_evaluation` | Safe Order Agent의 Scenario·Check·Trace·Regression |
| `09_integrated-agent-lab` | 별도 구성 예정 | 다음 과정의 통합 Mini Project |

## 선택 심화

| 자료 | 적용 위치 | 실행 결과 |
|---|---|---|
| Multimodal Agent | `optional_multimodal_agent` | 이미지 분석→Agent→승인→TTS 전체 연결 |

LangChain은 필수 단계에서 제외했습니다. 필요한 경우
`C:\aidevs\05_llm-agent-orchestration\00_references\10_optional-langchain-core`를
선택 자료로만 사용합니다.

## 수업 진행

```text
learning_unit 개념 예제
→ 여행 예제
→ starter 또는 steps 실습
→ Mock 테스트
→ 실제 Docker/Provider 선택 연결
→ Backend API 확인
→ Streamlit 화면 연결
→ 과제 도메인으로 변형
```

- 01~05는 `starter`에서 작성하고 `solution`과 비교합니다.
- 06은 완성된 독립 Single Agent 서비스에서 Agent별 Goal·Tool·종료를 비교하고 LangGraph는 선택 예제로 확인합니다.
- 07은 06의 Order Agent를 대표 사례로 승인 경계를 깊게 적용하고, 08은 그 Agent의
  저장된 실행 결과를 같은 평가 규칙으로 검사하고 실패 Trace를 확인합니다.
