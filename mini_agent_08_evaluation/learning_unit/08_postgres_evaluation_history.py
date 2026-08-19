"""평가 결과를 PostgreSQL JSONB와 요약 열에 함께 저장합니다."""

import json
import os
from datetime import datetime, timezone
from urllib.request import Request, urlopen

import psycopg
from psycopg.types.json import Jsonb


def run_evaluation(api_url: str) -> dict:
    """Backend의 반복 가능한 기본 평가를 실행합니다."""
    request = Request(f"{api_url.rstrip('/')}/api/evaluations/run", data=b'{"scenarios": []}', headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))["data"]


if __name__ == "__main__":
    result = run_evaluation(os.getenv("MINI_AGENT_API_URL", "http://localhost:8000"))
    summary = result["summary"]
    database_url = os.getenv("DATABASE_URL", "postgresql://agent_user:agent_password@127.0.0.1:5433/agent_db")
    with psycopg.connect(database_url) as connection:
        # JSONB는 실패 분석에, 개별 열은 빠른 통과율 조회에 사용합니다.
        connection.execute("CREATE TABLE IF NOT EXISTS evaluation_runs (id BIGSERIAL PRIMARY KEY, created_at TIMESTAMPTZ NOT NULL, provider TEXT NOT NULL, passed INTEGER NOT NULL, failed INTEGER NOT NULL, total INTEGER NOT NULL, pass_rate DOUBLE PRECISION NOT NULL, result JSONB NOT NULL)")
        run_id = connection.execute(
            "INSERT INTO evaluation_runs (created_at, provider, passed, failed, total, pass_rate, result) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
            (datetime.now(timezone.utc), os.getenv("LLM_PROVIDER", "mock"), summary["passed"], summary["failed"], summary["total"], summary["pass_rate"], Jsonb(result)),
        ).fetchone()[0]
        rows = connection.execute("SELECT id, provider, pass_rate, created_at FROM evaluation_runs ORDER BY id DESC LIMIT 5").fetchall()
    print({"saved_run_id": run_id, "recent_runs": rows})
