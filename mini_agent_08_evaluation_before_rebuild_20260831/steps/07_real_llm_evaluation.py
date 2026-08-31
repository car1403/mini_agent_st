"""learning_unit의 8-7 예제를 같은 순서로 실행합니다."""
from pathlib import Path
import runpy
runpy.run_path(Path(__file__).parents[1] / "learning_unit" / "07_real_llm_evaluation.py", run_name="__main__")
