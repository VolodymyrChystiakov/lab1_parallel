from __future__ import annotations

import argparse
from pathlib import Path

from benchmark import run_benchmark
from config import TEXT_DATA_DIR
from cpu_tasks import count_primes, factorize_many, generate_factorization_numbers, monte_carlo_pi
from io_tasks import count_words_parallel, count_words_sequential, generate_text_files
from memory_tasks import generate_matrix, transpose_checksum, transpose_parallel, transpose_sequential
from utils import timer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lab 1: sequential and parallel task processing")
    sub = parser.add_subparsers(dest="command", required=True)

    pi = sub.add_parser("pi")
    pi.add_argument("--iterations", type=int, default=500_000)
    pi.add_argument("--workers", type=int, default=1)
    pi.add_argument("--executor", choices=["thread", "process"], default="process")

    primes = sub.add_parser("primes")
    primes.add_argument("--limit", type=int, default=100_000)
    primes.add_argument("--workers", type=int, default=1)
    primes.add_argument("--executor", choices=["thread", "process"], default="process")

    fact = sub.add_parser("factorization")
    fact.add_argument("--numbers", type=int, default=20)
    fact.add_argument("--workers", type=int, default=1)
    fact.add_argument("--executor", choices=["thread", "process"], default="process")

    tr = sub.add_parser("transpose")
    tr.add_argument("--size", type=int, default=2000)
    tr.add_argument("--workers", type=int, default=1)

    gen = sub.add_parser("generate-texts")
    gen.add_argument("--files", type=int, default=1000)
    gen.add_argument("--words-per-file", type=int, default=250)
    gen.add_argument("--output", type=Path, default=TEXT_DATA_DIR)

    wc = sub.add_parser("wordcount")
    wc.add_argument("--directory", type=Path, default=TEXT_DATA_DIR)
    wc.add_argument("--workers", type=int, default=1)

    bench = sub.add_parser("benchmark")
    bench.add_argument("--profile", choices=["quick", "server"], default="quick")
    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "pi":
        with timer() as t:
            value = monte_carlo_pi(args.iterations, args.workers, args.executor)
        print(f"pi={value:.8f}")
        print(f"workers={args.workers}; executor={args.executor}; elapsed_ms={t['elapsed_ms']:.2f}")

    elif args.command == "primes":
        with timer() as t:
            value = count_primes(args.limit, args.workers, args.executor)
        print(f"prime_count={value}")
        print(f"workers={args.workers}; executor={args.executor}; elapsed_ms={t['elapsed_ms']:.2f}")

    elif args.command == "factorization":
        numbers = generate_factorization_numbers(args.numbers)
        with timer() as t:
            result = factorize_many(numbers, args.workers, args.executor)
        print(f"numbers={len(result)}; total_factors={sum(len(v) for v in result.values())}")
        print(f"workers={args.workers}; executor={args.executor}; elapsed_ms={t['elapsed_ms']:.2f}")

    elif args.command == "transpose":
        matrix = generate_matrix(args.size)
        with timer() as t:
            result = transpose_sequential(matrix) if args.workers <= 1 else transpose_parallel(matrix, args.workers)
        print(f"matrix={args.size}x{args.size}; checksum={transpose_checksum(result)}")
        print(f"workers={args.workers}; elapsed_ms={t['elapsed_ms']:.2f}")

    elif args.command == "generate-texts":
        with timer() as t:
            generate_text_files(args.output, args.files, args.words_per_file)
        print(f"generated_files={args.files}; directory={args.output}; elapsed_ms={t['elapsed_ms']:.2f}")

    elif args.command == "wordcount":
        with timer() as t:
            total = count_words_sequential(args.directory) if args.workers <= 1 else count_words_parallel(args.directory, args.workers)
        print(f"words={total}; directory={args.directory}")
        print(f"workers={args.workers}; elapsed_ms={t['elapsed_ms']:.2f}")

    elif args.command == "benchmark":
        csv_path = run_benchmark(args.profile)
        print(f"Benchmark completed: {csv_path}")


if __name__ == "__main__":
    main()
