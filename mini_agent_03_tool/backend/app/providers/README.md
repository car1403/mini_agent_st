# Providers

Provider는 OpenAI, Gemini, Ollama, Mock처럼 서로 다른 LLM API를 애플리케이션의 공통
호출·결과 계약으로 변환하는 Adapter 계층입니다.

## 담당하는 일

1. 공통 Prompt, Message와 Tool Definition을 모델별 요청 형식으로 변환합니다.
2. 선택된 모델 API를 한 번 호출합니다.
3. 모델별 응답을 공통 텍스트, 구조화 결과 또는 Tool Call로 정규화합니다.
4. Provider, 모델, 지연 시간과 원본 Tool Call 같은 통신 정보를 반환합니다.

## 담당하지 않는 일

- 어떤 Tool을 Agent에 제공할지 결정하지 않습니다.
- Tool arguments를 업무 규칙에 따라 추측하거나 보완하지 않습니다.
- Tool Allowlist 검증과 실제 함수를 실행하지 않습니다.
- 반복, 승인, 재시도와 종료 같은 Agent 정책을 결정하지 않습니다.

## 다른 계층과의 관계

```text
Router → Service ──────────────┐
                               ↓
                         Provider Adapter → LLM API
                               ↑
Router → Agent → Tool Selector ┘
               ↓
          Tool Executor → 실제 Tool
```

- 일반 생성과 Structured Output은 Service가 Provider를 호출합니다.
- Tool 선택 요청은 Agent가 Tool Definition과 함께 Provider를 호출합니다.
- Provider가 반환한 Tool Call은 Agent가 검증하고 Tool Executor에 전달합니다.

## 현재 구조

하나의 거대한 Gateway 대신 Provider별 Adapter와 공통 계약·레지스트리를 분리했습니다.

```text
providers/
├── __init__.py
├── base.py
├── models.py
├── registry.py
├── mock.py
├── openai.py
├── openai_media.py
├── gemini.py
└── ollama.py
```

Provider별 파일은 Tool Registry를 직접 import하지 않습니다. Agent가 사용할 Tool 목록을
인자로 전달하고 Provider는 이를 각 모델 API 형식으로 변환하기만 합니다.

Mock 모드의 Tool 선택은 외부 모델 Adapter가 아니라 `agents.mock_selector`가 실제 LLM의
판단을 재현합니다. 따라서 Mock Provider는 생성·구조화 응답을, Mock Selector는 교육용
Tool 판단을 각각 담당합니다.
