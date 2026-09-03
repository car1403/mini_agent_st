"""Mini Agent 07의 세 테이블과 상품 Seed를 PostgreSQL에 적용합니다."""

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


DATABASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DATABASE_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")

database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://agent_user:agent_password@127.0.0.1:5433/agent_db",
)

with psycopg.connect(database_url) as connection:
    connection.execute((DATABASE_DIR / "schema.sql").read_text(encoding="utf-8"))
    connection.execute((DATABASE_DIR / "seed.sql").read_text(encoding="utf-8"))

    table_count = connection.execute(
        """SELECT COUNT(*) FROM information_schema.tables
           WHERE table_schema = 'public'
             AND table_name IN ('products', 'order_agent_runs', 'orders')"""
    ).fetchone()[0]
    product_count = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]

print(f"주문 테이블 {table_count}/3개, 상품 Seed {product_count}개를 확인했습니다.")
