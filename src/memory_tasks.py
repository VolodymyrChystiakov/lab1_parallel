from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import numpy as np

from utils import chunk_ranges


def generate_matrix(size: int, seed: int = 42, dtype: str = "int32") -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 1000, size=(size, size), dtype=np.dtype(dtype))


def transpose_sequential(matrix: np.ndarray) -> np.ndarray:
    # copy() forces the operation to materialize instead of returning only a view
    return matrix.T.copy()


def _transpose_rows(args: tuple[np.ndarray, int, int]) -> tuple[int, int, np.ndarray]:
    matrix, start, end = args
    return start, end, matrix[start:end, :].T.copy()


def transpose_parallel(matrix: np.ndarray, workers: int = 1) -> np.ndarray:
    if workers <= 1:
        return transpose_sequential(matrix)

    size = matrix.shape[0]
    result = np.empty((size, size), dtype=matrix.dtype)
    ranges = chunk_ranges(0, size, workers)
    tasks = [(matrix, start, end) for start, end in ranges]

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for start, end, block_t in ex.map(_transpose_rows, tasks):
            result[:, start:end] = block_t
    return result


def transpose_checksum(matrix: np.ndarray) -> int:
    return int(matrix[0, 0]) + int(matrix[-1, -1]) + int(matrix[matrix.shape[0] // 2, matrix.shape[1] // 2])
