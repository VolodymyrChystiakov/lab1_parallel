from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def _load(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["elapsed_ms"] = pd.to_numeric(df["elapsed_ms"], errors="coerce")
    df["speedup"] = pd.to_numeric(df["speedup"], errors="coerce")
    return df


def _series_label(task: str, mode: str) -> str:
    return f"{task} / {mode}"


def _line_plot(
    df: pd.DataFrame,
    value_col: str,
    title: str,
    y_label: str,
    output_path: Path,
    *,
    log_y: bool = False,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    for (task, mode), group in df.groupby(["task", "mode"]):
        group = group.sort_values("workers")
        group = group.dropna(subset=[value_col])
        if group.empty:
            continue
        ax.plot(group["workers"], group[value_col], marker="o", label=_series_label(task, mode))

    ax.set_title(title)
    ax.set_xlabel("Workers")
    ax.set_ylabel(y_label)
    if log_y:
        ax.set_yscale("log")
        ax.set_ylabel(f"{y_label} (log scale)")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def save_time_plot(csv_path: Path, output_path: Path) -> None:
    df = _load(csv_path)
    _line_plot(df, "elapsed_ms", "Execution time by workers", "Time, ms", output_path)


def save_speedup_plot(csv_path: Path, output_path: Path) -> None:
    df = _load(csv_path)
    _line_plot(df, "speedup", "Speedup by workers", "Speedup", output_path)


def save_all_plots(csv_path: Path, plots_dir: Path) -> list[Path]:
    df = _load(csv_path)
    plots_dir.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []

    def add(name: str, data: pd.DataFrame, value: str, title: str, label: str, log_y: bool = False) -> None:
        path = plots_dir / name
        _line_plot(data, value, title, label, path, log_y=log_y)
        paths.append(path)

    cpu = df[df["task"].str.startswith("cpu_")]
    memory_io = df[df["task"].str.startswith(("memory_", "io_"))]

    add("execution_time_by_workers.png", df, "elapsed_ms", "Execution time by workers", "Time, ms")
    add("speedup_by_workers.png", df, "speedup", "Speedup by workers", "Speedup")
    add("execution_time_by_workers_log.png", df, "elapsed_ms", "Execution time by workers", "Time, ms", log_y=True)
    add("speedup_by_workers_log.png", df, "speedup", "Speedup by workers", "Speedup", log_y=True)

    if not cpu.empty:
        add("execution_time_cpu.png", cpu, "elapsed_ms", "CPU-bound tasks: execution time", "Time, ms")
        add("speedup_cpu.png", cpu, "speedup", "CPU-bound tasks: speedup", "Speedup")

    if not memory_io.empty:
        add("execution_time_memory_io.png", memory_io, "elapsed_ms", "Memory-bound and I/O-bound tasks: execution time", "Time, ms")
        add("speedup_memory_io.png", memory_io, "speedup", "Memory-bound and I/O-bound tasks: speedup", "Speedup")

    return paths
