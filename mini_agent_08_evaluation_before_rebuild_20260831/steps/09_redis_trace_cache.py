"""learning_unit의 8-9 예제를 같은 순서로 실행합니다."""
from pathlib import Path
import runpy
runpy.run_path(Path(__file__).parents[1] / "learning_unit" / "09_redis_trace_cache.py", run_name="__main__")
