from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
PLOTS_DIR = RESULTS_DIR / "plots"
TEXT_DATA_DIR = DATA_DIR / "generated_texts"


@dataclass(frozen=True)
class BenchmarkCase:
    task: str
    size_label: str
    workers: int
    mode: str
    elapsed_ms: float
    result: str
    speedup: float | None = None
