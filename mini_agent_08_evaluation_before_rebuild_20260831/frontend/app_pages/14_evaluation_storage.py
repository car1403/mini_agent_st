import json
import os
from datetime import datetime, timezone

import psycopg
import streamlit as st
from psycopg.types.json import Jsonb
from redis import Redis
from redis.exceptions import RedisError

from core.ui import backend_request, run_api


st.title("8-8~8-9. 평가 이력과 Trace 저장")
st.caption("PostgreSQL은 영구 이력, Redis는 최근 실패 Trace의 TTL 캐시를 담당합니다.")

evaluation = run_api(lambda: backend_request("POST", "/api/evaluations/run", {"scenarios": []})) if st.button("평가 실행") else None
if evaluation:
    st.session_state.latest_evaluation = evaluation
    st.json(evaluation["summary"])

latest = st.session_state.get("latest_evaluation")
if latest:
    col1, col2 = st.columns(2)
    with col1:
        if st.button("PostgreSQL에 영구 저장", use_container_width=True):
            try:
                summary = latest["summary"]
                with psycopg.connect(os.getenv("DATABASE_URL", "postgresql://agent_user:agent_password@127.0.0.1:5433/agent_db")) as connection:
                    connection.execute("CREATE TABLE IF NOT EXISTS evaluation_runs (id BIGSERIAL PRIMARY KEY, created_at TIMESTAMPTZ NOT NULL, provider TEXT NOT NULL, passed INTEGER NOT NULL, failed INTEGER NOT NULL, total INTEGER NOT NULL, pass_rate DOUBLE PRECISION NOT NULL, result JSONB NOT NULL)")
                    run_id = connection.execute("INSERT INTO evaluation_runs (created_at, provider, passed, failed, total, pass_rate, result) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id", (datetime.now(timezone.utc), os.getenv("LLM_PROVIDER", "mock"), summary["passed"], summary["failed"], summary["total"], summary["pass_rate"], Jsonb(latest))).fetchone()[0]
                st.success(f"evaluation_runs.id={run_id} 저장 완료")
            except psycopg.Error as error:
                st.error(f"PostgreSQL 연결 실패: {error}")
    with col2:
        if st.button("실패 Trace를 Redis에 캐시", use_container_width=True):
            try:
                client = Redis.from_url(os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0"), decode_responses=True)
                ttl = int(os.getenv("EVALUATION_TRACE_TTL_SECONDS", "600"))
                keys = []
                for index, result in enumerate(latest["results"], start=1):
                    if not result["passed"]:
                        key = f"evaluation:failed-trace:{index}"
                        client.setex(key, ttl, json.dumps(result["trace"], ensure_ascii=False))
                        keys.append(key)
                st.success(f"{len(keys)}개 Trace 캐시 완료 · TTL {ttl}초")
                st.json(keys)
            except (RedisError, ValueError) as error:
                st.error(f"Redis 연결 실패: {error}")
