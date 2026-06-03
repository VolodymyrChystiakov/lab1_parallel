from __future__ import annotations

import time
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def timer():
    start = time.perf_counter()
    box = {"elapsed_ms": 0.0}
    try:
        yield box
    finally:
        box["elapsed_ms"] = (time.perf_counter() - start) * 1000


def ensure_dirs(*paths: Path) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def chunk_ranges(start: int, end: int, chunks: int) -> list[tuple[int, int]]:
    total = max(0, end - start)
    chunks = max(1, min(chunks, total if total else 1))
    base = total // chunks
    extra = total % chunks
    ranges: list[tuple[int, int]] = []
    cur = start
    for i in range(chunks):
        step = base + (1 if i < extra else 0)
        ranges.append((cur, cur + step))
        cur += step
    return ranges
