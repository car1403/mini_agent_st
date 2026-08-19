"""learning_unit의 8-8 예제를 같은 순서로 실행합니다."""
from pathlib import Path
import runpy
runpy.run_path(Path(__file__).parents[1] / "learning_unit" / "08_postgres_evaluation_history.py", run_name="__main__")
