from __future__ import annotations

import random
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


_WORD_RE = re.compile(r"\b[\w']+\b", re.UNICODE)


def generate_text_files(directory: Path, files: int = 1000, words_per_file: int = 250, seed: int = 42) -> None:
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir(parents=True, exist_ok=True)

    rng = random.Random(seed)
    vocabulary = [
        "parallel", "thread", "process", "memory", "python", "file", "data", "task",
        "worker", "speed", "matrix", "number", "algorithm", "system", "cache", "disk",
    ]

    # A few nested folders make the recursive traversal meaningful.
    subdirs = [directory / f"part_{i:02d}" for i in range(10)]
    for subdir in subdirs:
        subdir.mkdir(parents=True, exist_ok=True)

    for i in range(files):
        target = subdirs[i % len(subdirs)] / f"text_{i:04d}.txt"
        words = [rng.choice(vocabulary) for _ in range(words_per_file)]
        target.write_text(" ".join(words), encoding="utf-8")


def list_text_files(directory: Path) -> list[Path]:
    return sorted(directory.rglob("*.txt"))


def count_words_in_file(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return len(_WORD_RE.findall(text))


def count_words_sequential(directory: Path) -> int:
    return sum(count_words_in_file(path) for path in list_text_files(directory))


def count_words_parallel(directory: Path, workers: int = 1) -> int:
    files = list_text_files(directory)
    if workers <= 1:
        return sum(count_words_in_file(path) for path in files)
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return sum(ex.map(count_words_in_file, files))
