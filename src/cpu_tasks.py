from __future__ import annotations

import math
import random
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Callable, Iterable

from utils import chunk_ranges


def _executor(kind: str, workers: int):
    if kind == "process":
        return ProcessPoolExecutor(max_workers=workers)
    return ThreadPoolExecutor(max_workers=workers)


# ---- Monte Carlo pi ----

def _pi_chunk(args: tuple[int, int]) -> int:
    iterations, seed = args
    rng = random.Random(seed)
    inside = 0
    for _ in range(iterations):
        x = rng.random()
        y = rng.random()
        if x * x + y * y <= 1.0:
            inside += 1
    return inside


def monte_carlo_pi(iterations: int, workers: int = 1, executor_type: str = "thread", seed: int = 42) -> float:
    if workers <= 1:
        inside = _pi_chunk((iterations, seed))
        return 4.0 * inside / iterations

    ranges = chunk_ranges(0, iterations, workers)
    args = [(b - a, seed + i * 1009) for i, (a, b) in enumerate(ranges)]
    with _executor(executor_type, workers) as ex:
        inside_total = sum(ex.map(_pi_chunk, args))
    return 4.0 * inside_total / iterations


# ---- Factorization ----

def factorize_number(n: int) -> list[int]:
    factors: list[int] = []
    while n % 2 == 0:
        factors.append(2)
        n //= 2
    d = 3
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 2
    if n > 1:
        factors.append(n)
    return factors


def factorize_many(numbers: list[int], workers: int = 1, executor_type: str = "thread") -> dict[int, list[int]]:
    if workers <= 1:
        return {n: factorize_number(n) for n in numbers}
    with _executor(executor_type, workers) as ex:
        values = list(ex.map(factorize_number, numbers))
    return dict(zip(numbers, values))


# ---- Prime numbers ----

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    limit = int(math.sqrt(n))
    d = 3
    while d <= limit:
        if n % d == 0:
            return False
        d += 2
    return True


def _count_primes_range(bounds: tuple[int, int]) -> int:
    start, end = bounds
    return sum(1 for n in range(start, end) if is_prime(n))


def count_primes(limit: int, workers: int = 1, executor_type: str = "thread") -> int:
    if workers <= 1:
        return _count_primes_range((2, limit + 1))
    ranges = chunk_ranges(2, limit + 1, workers)
    with _executor(executor_type, workers) as ex:
        return sum(ex.map(_count_primes_range, ranges))


def generate_factorization_numbers(count: int, seed: int = 42) -> list[int]:
    rng = random.Random(seed)
    base_primes = [1000003, 1000033, 1000037, 1000039, 1000081, 1000099, 1000117]
    numbers = []
    for _ in range(count):
        a = rng.choice(base_primes)
        b = rng.choice(base_primes)
        small = rng.randint(101, 997)
        numbers.append(a * b * small)
    return numbers
