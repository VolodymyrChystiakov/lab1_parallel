from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    cmd = [sys.executable, str(root / "src" / "main.py"), "benchmark", "--profile", "quick"]
    subprocess.run(cmd, check=True)
    print("Results:")
    print(root / "results" / "benchmark.csv")
    for plot in sorted((root / "results" / "plots").glob("*.png")):
        print(plot)


if __name__ == "__main__":
    main()
