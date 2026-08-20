# Mini Agent 03 · Tool Use

01~03에서 만든 화면과 API를 유지하면서 Tool 선택, 안전 실행, 최종 답변 생성을 추가한 누적형 완성본입니다.

```text
Streamlit app_pages
  → clients/agent_client.py
  → FastAPI routers/stage_01·02·03_router.py
  → agents/tool_selector.py가 Provider Adapter에 Tool Call 요청
  → 필수 arguments 누락 시 사용자에게 추가 질문
  → agents/tool_loop.py에서 단일 판단 Cycle 조정
  → tools/executor.py와 registry.py에서 검증·실행
  → Tool Result로 최종 답변
```

## 새로 배우는 내용

- Python 함수·Tool Schema·Tool Call·Tool Result
- 현재 날씨와 미래 예보 Tool의 선택 결과 비교
- `auto`·`none`·`required` Tool Choice
- Provider 원본 Tool Call과 정규화 결과
- 누락값을 추측하지 않는 추가 질문
- Pydantic arguments 검증
- Tool 선택과 실행 분리
- Allowlist 기반 안전 실행
- 공통 Tool 오류 코드
- Tool Result를 사용한 최종 답변
- Mock·Gemini·GPT·Ollama/Llama 비교

## 추가 메뉴

1. `Tool 선택`: 설명·Choice를 바꾸며 LLM의 원본 Tool Call과 정규화 결과를 확인합니다.
2. `Tool 실행`: arguments를 수정하고 Backend 검증 결과를 확인합니다.
3. `Agent Cycle`: 선택 → 재질문 또는 한 번 실행 → Tool Result → 최종 답변을 Trace로 확인합니다.

## Backend Router와 Swagger

기존 API URL은 유지하면서 Router를 과정 단계별로 분리했습니다.

- `stage_01_router.py`: LLM 기초·Provider·분류·Media
- `stage_02_router.py`: Prompt·Pydantic·Structured Output
- `stage_03_router.py`: Tool 선택·실행·단일 Agent Cycle

`http://127.0.0.1:8000/docs`에서도 같은 세 Tag로 구분되어 표시됩니다.

Schema도 Router 단계와 동일하게 분리합니다.

- `schemas/common.py`: Provider 이름과 공통 Message
- `schemas/stage_01.py`: LLM·분류·Media 계약
- `schemas/stage_02.py`: Prompt·Pydantic·Structured Output 계약
- `schemas/stage_03.py`: Tool arguments·선택·실행·Agent Cycle 계약

Schema 모델은 정의 위치를 분명히 알 수 있도록 각 Stage 모듈에서 직접 import합니다.

공통 환경 설정은 `core/config.py`에 두고 `.env`, 모델명, 외부 API URL과 제한값을
한곳에서 제공합니다. 이미지 분석과 음성 생성은 다음 경계로 분리합니다.

```text
stage_01_router
  → services/image_analysis_service.py 또는 speech_service.py
  → providers/openai_media.py
  → OpenAI Vision 또는 Speech API
```

Service는 입력 검증과 유스케이스를, Media Provider는 OpenAI SDK 요청·응답 변환을 담당합니다.

## Provider의 역할

Provider는 Agent가 아니라 OpenAI·Gemini·Ollama·Mock의 API 차이를 숨기는 Adapter입니다.
모델별 요청을 만들고 API를 한 번 호출한 뒤 텍스트·구조화 결과·Tool Call을 공통 형식으로
반환합니다. 사용할 Tool과 실행 순서는 `agents`, 실제 함수 실행은 `tools/executor.py`가
담당합니다. Provider는 Tool을 직접 실행하거나 Agent Loop를 소유하지 않습니다.

실행되는 Tool은 날씨·숙소·관광지 조회용 Mock 함수뿐입니다. 실제 예약, 결제, 환불, 삭제는 실행하지 않습니다.

## ToolSpec의 역할

`tools/registry.py`의 `ToolSpec`은 LLM에게 보여줄 Tool 설명과 Backend가 실행할 함수를
연결하는 단일 등록 단위입니다. 이름·설명·Pydantic 입력 모델·실행 함수를 한곳에 등록하고,
같은 입력 모델에서 LLM용 JSON Schema와 실행 직전 검증을 모두 생성합니다.

## 실행

```powershell
cd C:\mini_agent_st\mini_agent_03_tool
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env

cd backend
uvicorn app.main:app --reload --port 8000
```

새 터미널에서 실행합니다.

```powershell
cd C:\mini_agent_st\mini_agent_03_tool
.\.venv\Scripts\Activate.ps1
streamlit run .\frontend\app.py
```

기본 Provider는 Mock입니다. 먼저 Mock으로 단일 Agent Cycle을 확인한 다음 준비된 Provider만 선택적으로 비교합니다.

현재 과정은 Tool 하나를 선택하고 최대 한 번 실행하는 Cycle까지 다룹니다. 여러 Tool을
반복 호출하는 Agent Loop는 이후 과정에서 최대 반복 횟수와 종료 조건을 함께 추가합니다.

## 실제 날씨 Tool

날씨 Tool은 현재 상태와 미래 예보를 구분합니다.

- `get_current_weather`: 현재 기온·체감 온도·강수량·바람
- `get_weather_forecast`: 지정한 미래 날짜의 최고·최저 기온과 강수 확률

기본 `WEATHER_MODE=mock`은 인터넷 없이 결정적으로 실행됩니다. `.env`에서 다음과
같이 바꾸면 Tool 실행 단계가 Open-Meteo Geocoding API와 Forecast API를 호출합니다.

```env
WEATHER_MODE=open_meteo
```

Open-Meteo의 현재 상태는 관측소 실측값이 아니라 최신 기상 모델 기반 값입니다.
외부 API 오류가 발생하면 실제 값처럼 Mock으로 조용히 대체하지 않고 Tool 오류를
반환합니다.
