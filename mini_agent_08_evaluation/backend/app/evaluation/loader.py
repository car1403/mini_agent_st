import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_suite() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    scenarios = _load(ROOT / "data" / "scenarios.json")
    results = _load(ROOT / "data" / "results.json")
    return scenarios, results
