# 선택 비교 · 같은 Travel Agent를 LangGraph로 실행

메인 서비스는 `backend/app/agents/runtime.py`의 순수 Python Loop를 사용합니다. 이 폴더는 같은 Travel Agent Profile, OpenAI Model과 HTTP MCP Tool을 LangGraph의 State·Node·Edge로 표현한 비교 예제입니다.

```text
메인: Python for Loop → Model → MCP Tool → Model
선택: LangGraph Agent Node → MCP Tool Node → Agent Node → END
```

LangGraph가 새로운 Agent를 만드는 것은 아닙니다. 같은 Agent Runtime의 실행 구조만 달라집니다.

```powershell
python .\10_optional_langgraph\travel_agent_graph.py
```
