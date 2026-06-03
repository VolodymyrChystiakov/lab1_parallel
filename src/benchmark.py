from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from config import PLOTS_DIR, RESULTS_DIR, TEXT_DATA_DIR
from cpu_tasks import count_primes, factorize_many, generate_factorization_numbers, monte_carlo_pi
from io_tasks import count_words_parallel, count_words_sequential, generate_text_files
from memory_tasks import generate_matrix, transpose_checksum, transpose_parallel, transpose_sequential
from plots import save_all_plots
from utils import ensure_dirs, timer


PROFILES: dict[str, dict[str, Any]] = {
    "quick": {
        "workers": [1, 2, 4, 8],
        "pi_iterations": 200_000,
        "prime_limit": 60_000,
        "factor_numbers": 24,
        "matrix_size": 1200,
        "text_files": 250,
        "words_per_file": 150,
    },
    "server": {
        "workers": [1, 2, 4, 8],
        "pi_iterations": 2_000_000,
        "prime_limit": 250_000,
        "factor_numbers": 80,
        "matrix_size": 5000,
        "text_files": 1000,
        "words_per_file": 250,
    },
}


def _write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["task", "mode", "workers", "size", "elapsed_ms", "speedup", "result"],
        )
        writer.writeheader()
        writer.writerows(rows)


def _add_speedups(rows: list[dict[str, Any]]) -> None:
    baseline: dict[str, float] = {}
    for row in rows:
        if row["workers"] == 1 and row["mode"] == "sequential":
            baseline[row["task"]] = row["elapsed_ms"]
    for row in rows:
        base = baseline.get(row["task"])
        row["speedup"] = round(base / row["elapsed_ms"], 4) if base and row["elapsed_ms"] else ""


def run_benchmark(profile: str = "quick") -> Path:
    if profile not in PROFILES:
        raise ValueError(f"Unknown benchmark profile: {profile}. Available: {', '.join(PROFILES)}")

    cfg = PROFILES[profile]
    ensure_dirs(RESULTS_DIR, PLOTS_DIR, TEXT_DATA_DIR)
    rows: list[dict[str, Any]] = []
    workers_list = cfg["workers"]

    # CPU-bound: Monte Carlo pi
    iterations = cfg["pi_iterations"]
    for workers in workers_list:
        mode = "sequential" if workers == 1 else "process"
        with timer() as t:
            pi = monte_carlo_pi(iterations, workers=workers, executor_type=("process" if workers > 1 else "thread"))
        rows.append({
            "task": "cpu_pi",
            "mode": mode,
            "workers": workers,
            "size": f"iterations={iterations}",
            "elapsed_ms": round(t["elapsed_ms"], 2),
            "speedup": "",
            "result": f"pi={pi:.6f}",
        })

    # CPU-bound: primes
    limit = cfg["prime_limit"]
    for workers in workers_list:
        mode = "sequential" if workers == 1 else "process"
        with timer() as t:
            count = count_primes(limit, workers=workers, executor_type=("process" if workers > 1 else "thread"))
        rows.append({
            "task": "cpu_primes",
            "mode": mode,
            "workers": workers,
            "size": f"limit={limit}",
            "elapsed_ms": round(t["elapsed_ms"], 2),
            "speedup": "",
            "result": f"count={count}",
        })

    # CPU-bound: factorization
    numbers = generate_factorization_numbers(cfg["factor_numbers"])
    for workers in workers_list:
        mode = "sequential" if workers == 1 else "process"
        with timer() as t:
            factors = factorize_many(numbers, workers=workers, executor_type=("process" if workers > 1 else "thread"))
        total_factors = sum(len(v) for v in factors.values())
        rows.append({
            "task": "cpu_factorization",
            "mode": mode,
            "workers": workers,
            "size": f"numbers={len(numbers)}",
            "elapsed_ms": round(t["elapsed_ms"], 2),
            "speedup": "",
            "result": f"factors={total_factors}",
        })

    # Memory-bound: matrix transpose
    size = cfg["matrix_size"]
    matrix = generate_matrix(size)
    base_checksum = transpose_checksum(matrix)
    for workers in workers_list:
        mode = "sequential" if workers == 1 else "thread"
        with timer() as t:
            transposed = transpose_sequential(matrix) if workers == 1 else transpose_parallel(matrix, workers=workers)
        rows.append({
            "task": "memory_transpose",
            "mode": mode,
            "workers": workers,
            "size": f"matrix={size}x{size}",
            "elapsed_ms": round(t["elapsed_ms"], 2),
            "speedup": "",
            "result": f"checksum={transpose_checksum(transposed)};source={base_checksum}",
        })

    # I/O-bound: recursive word count
    files = cfg["text_files"]
    words_per_file = cfg["words_per_file"]
    generate_text_files(TEXT_DATA_DIR, files=files, words_per_file=words_per_file)
    for workers in workers_list:
        mode = "sequential" if workers == 1 else "thread"
        with timer() as t:
            total = count_words_sequential(TEXT_DATA_DIR) if workers == 1 else count_words_parallel(TEXT_DATA_DIR, workers)
        rows.append({
            "task": "io_wordcount",
            "mode": mode,
            "workers": workers,
            "size": f"files={files};words_per_file={words_per_file}",
            "elapsed_ms": round(t["elapsed_ms"], 2),
            "speedup": "",
            "result": f"words={total}",
        })

    _add_speedups(rows)
    csv_path = RESULTS_DIR / "benchmark.csv"
    _write_rows(csv_path, rows)
    save_all_plots(csv_path, PLOTS_DIR)
    return csv_path


def run_default_benchmark() -> Path:
    return run_benchmark("quick")
